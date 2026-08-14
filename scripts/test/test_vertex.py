import os
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image

# Set dummy key for import
os.environ["POKEMON_API_KEY"] = "testkey"

from app.pokemon_api import PokemonBase
from app.vertex_classifier import VertexClassifier

class TestVertexClassifier(unittest.TestCase):
    def setUp(self):
        # Create a mock pokemon repository
        self.pokemon_repo = MagicMock(spec=PokemonBase)
        # Mock get_all_names to return a set of names
        self.pokemon_repo.get_all_names.return_value = {"Pikachu", "Bulbasaur", "Charmander"}
        # Mock get_by_name to return a dummy pokemon info dict
        self.pokemon_repo.get_by_name.side_effect = lambda name: {
            "name": name.capitalize(),
            "id": 25 if name.lower() == "pikachu" else 1
        }

    @patch("app.vertex_classifier.genai.Client")
    def test_classify_image_success(self, mock_client_cls):
        # Mock Client and models
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "This looks like a Pikachu!"
        mock_client.models.generate_content.return_value = mock_response
        
        classifier = VertexClassifier(pokemon_repo=self.pokemon_repo)
        
        # Create a dummy image
        img = Image.new('RGB', (10, 10), color='red')
        result = classifier.classify_image(img)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Pikachu")
        self.pokemon_repo.get_by_name.assert_called_with("Pikachu")

    @patch("app.vertex_classifier.genai.Client")
    def test_classify_image_no_match(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "I don't know what this is, maybe a red circle."
        mock_client.models.generate_content.return_value = mock_response
        
        classifier = VertexClassifier(pokemon_repo=self.pokemon_repo)
        
        img = Image.new('RGB', (10, 10), color='red')
        result = classifier.classify_image(img)
        
        self.assertIsNone(result)

    @patch("app.vertex_classifier.genai.Client")
    def test_client_initialization_with_api_key(self, mock_client_cls):
        test_env = dict(os.environ)
        test_env["GEMINI_API_KEY"] = "dummy_api_key"
        
        with patch.dict(os.environ, test_env, clear=True):
            classifier = VertexClassifier(pokemon_repo=self.pokemon_repo)
            _ = classifier.client
            mock_client_cls.assert_called_once_with(api_key="dummy_api_key")

    @patch("app.vertex_classifier.genai.Client")
    def test_client_initialization_with_gcloud_creds(self, mock_client_cls):
        test_env = dict(os.environ)
        if "GEMINI_API_KEY" in test_env:
            del test_env["GEMINI_API_KEY"]
        test_env["GOOGLE_APPLICATION_CREDENTIALS"] = "/dummy/cred.json"
        
        with patch.dict(os.environ, test_env, clear=True):
            classifier = VertexClassifier(pokemon_repo=self.pokemon_repo)
            _ = classifier.client
            mock_client_cls.assert_called_once_with(
                vertexai=True,
                project=classifier.project,
                location=classifier.location
            )

if __name__ == "__main__":
    unittest.main()
