import csv

# Comprehensive mapping dictionary for complex, legendary, and easily mispronounced Pokémon across all generations.
# Fallback logic handles standard English phonetic rules for simpler names.
SPECIAL_PHONETICS = {
    "Bulbasaur": "BUL-buh-sore", "Ivysaur": "EYE-vee-sore", "Venusaur": "VEE-nuh-sore",
    "Charmander": "CHAR-man-der", "Charmeleon": "char-MEE-lee-un", "Charizard": "CHAR-ih-zard",
    "Squirtle": "SKWER-tul", "Wartortle": "WAR-tor-tul", "Blastoise": "BLAS-toys",
    "Pikachu": "PEE-kah-choo", "Raichu": "RYE-choo", "Nidoran♀": "NEE-doh-ran female",
    "Nidoran♂": "NEE-doh-ran male", "Vulpix": "VUL-piks", "Ninetales": "NINE-tayls",
    "Jigglypuff": "JIG-lee-puf", "Meowth": "mee-OWTH", "Psyduck": "SIGH-duk",
    "Growlithe": "GROW-lith", "Arcanine": "AR-kuh-nine", "Alakazam": "AL-ah-kuh-zam",
    "Ponyta": "poh-NEE-tah", "Rapidash": "RAP-ih-dash", "Slowpoke": "SLOH-pohk",
    "Gengar": "GEN-gar", "Gyarados": "GARE-uh-dose", "Lapras": "LAP-ras",
    "Eevee": "EE-vee", "Vaporeon": "vay-POR-ee-un", "Jolteon": "JOL-tee-un",
    "Flareon": "FLAIR-ee-un", "Porygon": "POR-ee-gon", "Aerodactyl": "air-oh-DAK-tul",
    "Snorlax": "SNOR-laks", "Articuno": "ar-tih-KOO-noh", "Zapdos": "ZAP-dose",
    "Moltres": "MOL-tres", "Dratini": "druh-TEE-nee", "Dragonair": "drag-un-AIR",
    "Dragonite": "DRAG-un-ite", "Mewtwo": "MYOO-too", "Mew": "MYOO",
    "Chikorita": "chik-uh-REE-tah", "Cyndaquil": "SIN-duh-kwil", "Totodile": "TOH-toh-dile",
    "Togepi": "TOH-geh-pee", "Mareep": "muh-REEP", "Sudowoodo": "soo-doh-WOO-doh",
    "Espeon": "ES-pee-un", "Umbreon": "UM-bree-un", "Wobbuffet": "WAH-buh-fet",
    "Scizor": "SIZE-or", "Heracross": "HAIR-uh-kros", "Skarmory": "SKAR-mor-ee",
    "Houndoom": "HOWN-doom", "Kingdra": "KING-druh", "Raikou": "RYE-koo",
    "Entei": "EN-tay", "Suicune": "SWEE-koon", "Tyranitar": "tye-RAN-ih-tar",
    "Lugia": "LOO-gee-uh", "Ho-Oh": "HOH-oh", "Celebi": "SEL-eh-bee",
    "Treecko": "TREE-koh", "Torchic": "TOR-chik", "Mudkip": "MUD-kip",
    "Gardevoir": "GAR-deh-vwahr", "Shedinja": "sheh-DIN-juh", "Sableye": "SAY-bul-eye",
    "Mawile": "MAW-wile", "Milotic": "my-LAH-tik", "Absol": "AB-sol",
    "Salamence": "SAL-uh-mens", "Metagross": "MET-uh-gros", "Latias": "LAH-tee-as",
    "Latios": "LAH-tee-os", "Kyogre": "kye-OH-ger", "Groudon": "GROW-don",
    "Rayquaza": "ray-KWAY-zah", "Jirachi": "jih-RAH-chee", "Deoxys": "dee-OK-sis",
    "Lucario": "loo-KAR-ee-oh", "Garchomp": "GAR-chomp", "Rotom": "ROH-tom",
    "Dialga": "dee-AL-guh", "Palkia": "PAL-kee-uh", "Heatran": "HEE-tran",
    "Regigigas": "reh-jee-JIH-gus", "Giratina": "gih-ruh-TEE-nuh", "Cresselia": "kruh-SEL-ee-uh",
    "Darkrai": "DARK-rye", "Arceus": "AR-kee-us", "Victini": "vik-TEE-nee",
    "Snivy": "SNY-vee", "Tepig": "TEH-pig", "Oshawott": "OSH-uh-wot",
    "Zorua": "ZOR-oo-uh", "Zoroark": "ZOR-oh-ark", "Chandelure": "shand-uh-LOOR",
    "Hydreigon": "hye-DRY-gon", "Cobalion": "koh-BAY-lee-un", "Terrakion": "tuh-RAY-kee-un",
    "Virizion": "vih-RYE-zee-un", "Reshiram": "RESH-ih-ram", "Zekrom": "ZEK-rom",
    "Landorus": "lan-DOR-us", "Kyurem": "KYOO-rem", "Keldeo": "kel-DEE-oh",
    "Meloetta": "mel-oh-ET-uh", "Genesect": "JEN-uh-sekt", "Greninja": "greh-NIN-juh",
    "Aegislash": "EE-jih-slash", "Sylveon": "SIL-vee-un", "Goodra": "GOO-druh",
    "Noivern": "NOY-vern", "Xerneas": "ZUR-nee-us", "Yveltal": "ee-VEL-tall",
    "Zygarde": "ZYE-gard", "Diancie": "dye-AN-see", "Hoopa": "HOO-puh",
    "Volcanion": "vol-KAY-nee-un", "Lycanroc": "lye-KAN-rok", "Toxapex": "tok-SAY-peks",
    "Mimikyu": "MIM-ih-kyoo", "Tapu Koko": "TAH-poo KOH-koh", "Tapu Lele": "TAH-poo LEH-leh",
    "Solgaleo": "sol-guh-LAY-oh", "Lunala": "loo-NAH-lah", "Nihilego": "nye-hee-LAY-goh",
    "Buzzwole": "BUZ-wohl", "Pheromosa": "fair-uh-MOH-suh", "Xurkitree": "ZER-kih-tree",
    "Celesteela": "seh-les-TEE-luh", "Kartana": "kar-TAH-nuh", "Guzzlord": "GUZ-lord",
    "Necrozma": "neh-KROZ-muh", "Magearna": "muh-GEER-nuh", "Marshadow": "MAR-shad-oh",
    "Zeraora": "zeh-ruh-OR-uh", "Corviknight": "KOR-vih-nite", "Toxtricity": "tok-TRIS-ih-tee",
    "Sirfetch'd": "ser-FECH-t", "Zacian": "ZAH-shee-un", "Zamazenta": "zah-muh-ZEN-tah",
    "Eternatus": "ee-TER-nuh-tus", "Urshifu": "ER-shih-foo", "Regieleki": "reh-jee-el-EK-ee",
    "Regidrago": "reh-jee-DRAY-goh", "Calyrex": "KAL-ih-reks", "Sprigatito": "spree-gah-TEE-toh",
    "Fuecoco": "fway-KOH-koh", "Quaxly": "KWAK-slee", "Lechonk": "leh-CHONK",
    "Koraidon": "kor-EYE-don", "Miraidon": "mee-RYE-don"
}

def clean_name_for_tts(name):
    # Strip annoying punctuation that hitches up Flite/Piper tokenizers
    return name.replace("'", "").replace(".", "").replace(":", "").strip()

def normalize_name(name):
    # Convert gender symbols to the standard PokéAPI format
    n = name.lower()
    n = n.replace("♀", "-f").replace("♂", "-m")
    # Strip apostrophes, periods, and colons
    n = n.replace("'", "").replace(".", "").replace(":", "")
    # Replace spaces with hyphens
    n = n.replace(" ", "-")
    return n

def generate_fallback_phonetic(name):
    # Generates a safe, space/hyphen split string for plain names
    # to guarantee Piper and Flite don't stumble on composite words.
    cleaned = clean_name_for_tts(name)
    
    # If the name is already composite/hyphenated, split and process parts individually
    if "-" in cleaned:
        parts = cleaned.split("-")
        return "-".join(generate_fallback_phonetic(part) for part in parts if part)
        
    if len(cleaned) <= 4:
        return cleaned.upper()
    
    # Syllable/chunking helper
    vowels = "aeiouyAEIOUY"
    chunks = []
    current_chunk = ""
    
    for i, char in enumerate(cleaned):
        current_chunk += char
        if i < len(cleaned) - 1:
            curr_is_vowel = char in vowels
            next_is_vowel = cleaned[i+1] in vowels
            
            if curr_is_vowel and not next_is_vowel:
                chunks.append(current_chunk)
                current_chunk = ""
            elif not curr_is_vowel and not next_is_vowel and char.lower() != cleaned[i+1].lower():
                chunks.append(current_chunk)
                current_chunk = ""
                
    if current_chunk:
        chunks.append(current_chunk)
        
    final_chunks = []
    temp = ""
    for c in chunks:
        temp += c
        if len(temp) >= 3 or (len(temp) >= 2 and any(v in temp for v in vowels)):
            final_chunks.append(temp.upper())
            temp = ""
    if temp:
        if final_chunks:
            final_chunks[-1] += temp.upper()
        else:
            final_chunks.append(temp.upper())
            
    return "-".join(final_chunks)

# -------------------------------------------------------------
# RUN ENGINE GENERATION
# -------------------------------------------------------------
import pokebase as pb
import os

def run_generation():
    output_path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "pokemon_tts_phonetics.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print("Fetching full National Dex from PokéAPI...")
    try:
        # Pre-normalize the special phonetics dictionary
        norm_special = {normalize_name(k): v for k, v in SPECIAL_PHONETICS.items()}
        
        # Fetching all pokemon names
        pokedex = pb.APIResourceList('pokemon')
        
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Phonetic_TTS'])
            
            count = 0
            for entry in pokedex:
                # Name from PokéAPI is usually lowercase (e.g. 'bulbasaur', 'nidoran-f', 'ho-oh')
                raw_name = entry['name']
                name_parts = raw_name.split('-')
                display_name = "-".join(part.capitalize() for part in name_parts)
                
                pk_id = entry['url'].split('/')[-2]
                
                norm_name = normalize_name(raw_name)
                phonetic = None
                
                # 1. Exact match in normalized special phonetics
                if norm_name in norm_special:
                    phonetic = norm_special[norm_name]
                else:
                    # 2. Check if it matches a prefix of form suffixes (e.g., 'deoxys-normal' -> 'deoxys')
                    for i in range(len(name_parts) - 1, 0, -1):
                        prefix = "-".join(name_parts[:i])
                        norm_prefix = normalize_name(prefix)
                        if norm_prefix in norm_special:
                            suffix = "-".join(name_parts[i:])
                            phonetic = f"{norm_special[norm_prefix]}-{suffix.upper()}"
                            break
                
                # 3. Fallback to chunking
                if not phonetic:
                    phonetic = generate_fallback_phonetic(display_name)
                
                writer.writerow([pk_id, display_name, phonetic])
                count += 1
            
            print(f"Successfully generated {count} entries in {output_path}")
            
    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    print("Generating full database mapping...")
    run_generation()