import os
import json
import re

def update_python_and_settings(lang_code):
    lang_upper = lang_code.upper()
    lang_lower = lang_code.lower()

    # 1. Update json2str.py
    with open("json2str.py", "r", encoding="utf-8") as f:
        j2s = f.read()

    if f"'{lang_upper}:'" not in j2s and f'"{lang_upper}:"' not in j2s:
        # Inject into language_prefixes comprehension array safely
        j2s = re.sub(r"(\['US', 'DE'.*?)(\])", r"\1, '" + lang_upper + r"'\2", j2s)
        # Inject into file_to_lang dict
        j2s = re.sub(r"(file_to_lang\s*=\s*\{.*?)(\s*\})", r"\1, '" + lang_lower + "': '" + lang_upper + ":'\2", j2s, flags=re.DOTALL)
        with open("json2str.py", "w", encoding="utf-8") as f:
            f.write(j2s)

    # 2. Update str2json.py
    with open("str2json.py", "r", encoding="utf-8") as f:
        s2j = f.read()

    if f"'{lang_upper}'" not in s2j and f'"{lang_upper}"' not in s2j:
        s2j = re.sub(r"(language_codes\s*=\s*\[.*?)(\])", r"\1, '" + lang_upper + r"'\2", s2j)
        with open("str2json.py", "w", encoding="utf-8") as f:
            f.write(s2j)

    # 3. Update project.inlang/settings.json
    settings_path = os.path.join("project.inlang", "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)

        if lang_lower not in settings.get("languageTags", []):
            settings["languageTags"].append(lang_lower)
            settings["languageTags"].sort() # Keep alphabetized
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

def process_imports():
    imports_dir = "imports"
    loc_dir = "localization"
    if not os.path.exists(imports_dir):
        return

    for lang_code in os.listdir(imports_dir):
        lang_dir = os.path.join(imports_dir, lang_code)
        if not os.path.isdir(lang_dir):
            continue

        lang_upper = lang_code.upper()
        json_path = os.path.join(loc_dir, f"{lang_code.lower()}.json")

        # Load existing JSON or create empty dict
        translations = {}
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)

        files_found = False
        # Parse legacy .str files
        for file in os.listdir(lang_dir):
            if not file.endswith('.str'): continue
            files_found = True

            filepath = os.path.join(lang_dir, file)
            current_label = None

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("//"):
                        continue

                    if ":" in stripped and not any(c in stripped for c in [' ', '"']):
                        current_label = stripped
                    elif current_label and stripped != "END":
                        parts = stripped.split(':', 1)
                        if len(parts) == 2 and parts[0].strip().upper() == lang_upper:
                            text = parts[1].strip()
                            if text.startswith('"') and text.endswith('"'): text = text[1:-1]
                            # Clean up escaping for json
                            text = text.replace('\\"', '"')
                            translations[current_label] = text
                    elif stripped == "END":
                        current_label = None

        if files_found:
            os.makedirs(loc_dir, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=4, ensure_ascii=False)
            print(f"Imported and mapped {lang_code.upper()} language.")
            update_python_and_settings(lang_code)

if __name__ == "__main__":
    process_imports()