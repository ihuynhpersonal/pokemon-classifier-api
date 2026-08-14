import io
import logging
import os
import re
from PIL import Image
from google import genai
from google.genai import types
from pydantic import BaseModel

from .pokemon_api import PokemonBase

logger = logging.getLogger(__name__)

class PokemonIdentification(BaseModel):
    visual_reasoning: str
    pokemon_name: str

class VertexClassifier:
    def __init__(self, pokemon_repo: PokemonBase = None):
        self.pokemon_repo = pokemon_repo if pokemon_repo is not None else PokemonBase()
        self._client = None
        self.project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
        self.model_name = os.getenv("VERTEX_MODEL_NAME", "gemini-3.5-flash-lite")

    @property
    def client(self) -> genai.Client:
        """Lazily initialize the google-genai Client."""
        if self._client is None:
            self._client = genai.Client(
                vertexai=True,
                project=self.project,
                location=self.location
            )
        return self._client

    def find_pokemon_in_response(self, text: str) -> str | None:
        """
        Parses the model's text response and returns the name of the matched Pokémon if found.
        """
        if not text:
            return None
            
        pokemon_names = self.pokemon_repo.get_all_names()
        if not pokemon_names:
            logger.warning("No Pokémon names loaded in repository.")
            return None

        # Build name mappings and compiled regex
        name_map = {name.lower(): name for name in pokemon_names}
        sorted_names = sorted(pokemon_names, key=len, reverse=True)
        escaped_names = [re.escape(name.lower()) for name in sorted_names]
        pattern_str = r'\b(' + '|'.join(escaped_names) + r')\b'
        pokemon_regex = re.compile(pattern_str, re.IGNORECASE)

        # Search the entire response text for any known Pokémon name
        match = pokemon_regex.search(text)
        if match:
            matched_name = name_map.get(match.group(1).lower())
            logger.info(f"Found Pokémon in Vertex AI text response: {matched_name}")
            return matched_name

        return None

    def classify_image(self, image: Image.Image | bytes) -> dict | None:
        """
        Classifies the Pokémon in the image using Vertex AI Gemini.
        Returns the enriched Pokémon data dict, or None if classification failed.
        """
        try:
            if isinstance(image, Image.Image):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                image_bytes = img_byte_arr.getvalue()
                mime_type = 'image/png'
            else:
                image_bytes = image
                # Basic magic number mime detection
                if image_bytes.startswith(b"\xff\xd8"):
                    mime_type = 'image/jpeg'
                elif image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                    mime_type = 'image/png'
                elif image_bytes.startswith(b"GIF8"):
                    mime_type = 'image/gif'
                elif image_bytes.startswith(b"RIFF") and b"WEBP" in image_bytes[8:12]:
                    mime_type = 'image/webp'
                else:
                    mime_type = 'image/png'

            logger.info(f"Querying Vertex AI model={self.model_name}...")
            
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image_part,
                    "Analyze this exhibit photo from the Pokémon Fossil Museum and identify the Pokémon shown.",
                ],
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are an expert Pokémon taxonomy model analyzing exhibit photos from the Pokémon Fossil Museum. "
                        "The input image is a low-resolution capture from a Nintendo 3DS camera. Expect noise, dark shadows, and pixelation. "
                        "EXHIBIT TYPES: Displays may feature full-color 3D sculptures, life-sized skeletal reconstructions, 2D infographic signs, "
                        "or real-world fossils shown alongside Pokémon art (e.g., Tyrantrum vs T. rex, Aerodactyl vs Pterosaur). "
                        "ANALYSIS GUIDELINES: "
                        "1. Focus on overall body plan (bipedal, quadrupedal, avian, aquatic, head frills, jaw/teeth structure, tail geometry, wing bones). "
                        "2. If a real-world fossil or animal replica is shown next to a Pokémon illustration or model, identify the featured Pokémon. "
                        "3. Do not guess Cubone or Marowak purely because a skull, skeleton, or bone structure is present. "
                        "4. If Excavator/Fossil Pikachu is present, identify as 'Pikachu'. "
                        "5. If no Pokémon is present or identifiable in the frame, set pokemon_name to 'None'."
                    ),
                    response_mime_type="application/json",
                    response_schema=PokemonIdentification,
                ),
            )

            result = PokemonIdentification.model_validate_json(response.text)
            logger.info(f"Vertex AI Raw Response: {response.text}")

            pokemon_name = result.pokemon_name
            if pokemon_name:
                logger.info(f"Vertex AI successfully classified image as: {pokemon_name}")
                return self.pokemon_repo.get_by_name(pokemon_name)

            logger.info("Vertex AI did not find any matching Pokémon in the response.")
            return None

        except Exception as e:
            logger.error(f"Error during Vertex AI classification: {e}", exc_info=True)
            return None
