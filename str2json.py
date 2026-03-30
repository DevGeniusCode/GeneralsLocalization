import os
import json
import re

# List of language codes we expect to encounter
# CTX stands for 'context' and is used to store context data for each label if provided
language_codes = ['US', 'DE', 'FR', 'ES', 'IT', 'KO', 'ZH', 'BP', 'PL', 'RU', 'AR', 'UK', 'CTX', 'HE']

# List of format specifiers
format_specifiers = [
    "%u", "%c", "%s", "%S", "%ls", "%hs", "%.0f%%", "%d", "%dms", "%d%%", "%d:0%d",
    "%d.%02d", "%d:%2.2d", "%d.%02d.%d", "%d:%02d:%02d", "\\n"
]

format_regex = re.compile(r'(' + '|'.join(map(re.escape, format_specifiers)) + r')')

def apply_format_specifiers(text):
    """ Apply curly braces around format specifiers in the text, including '&' with adjacent characters """
    text = re.sub(r'&(\w)', r'{&\1}', text)
    text = format_regex.sub(r'{\1}', text)
    return text

def parse_file(input_file):
    translations = {lang: {} for lang in language_codes}

    with open(input_file, 'r', encoding='utf-8') as file:
        current_label = None
        current_context = "TODO"
        sub_label_name = ""  # <-- NEW: Tracks if we are in core/optional block

        for line in file:
            raw_stripped = line.strip()

            if not raw_stripped:
                continue

            # 1. Handle lines that are strictly comments (start with //)
            if raw_stripped.startswith('//'):
                # Track core/optional blocks
                if "patch104p-core-begin" in raw_stripped or "patch104p-optional-begin" in raw_stripped:
                    sub_label_name = raw_stripped
                elif "patch104p-core-end" in raw_stripped or "patch104p-optional-end" in raw_stripped:
                    sub_label_name = ""

                if raw_stripped.lower().startswith('// context:'):
                    # Found the start of a context block
                    new_context_part = raw_stripped.split(':', 1)[1].strip()
                    if current_context == "TODO":
                        current_context = new_context_part
                    else:
                        current_context += " " + new_context_part
                else:
                    # Found a regular comment line starting with //.
                    # If we are collecting context (and haven't reached a label yet), append it.
                    if current_context != "TODO" and current_label is None:
                        # Only append to context if it's not a patch-specific system tag
                        if "patch104p-" not in raw_stripped:
                            extra_text = raw_stripped[2:].strip()  # Remove the //
                            if extra_text:
                                current_context += " " + extra_text

                # Finished processing this comment line, move to the next
                continue

            # 2. Clean up inline comments at the end of the line
            stripped_line = raw_stripped.split('//')[0].strip()
            if not stripped_line:
                continue

            # 3. Identify a Label
            if ':' in stripped_line and not any(c in stripped_line for c in [' ', '"']):
                current_label = stripped_line
                # Save the collected context under this label
                translations['CTX'][current_label] = current_context

            # 4. Identify a translation line
            elif current_label and stripped_line != "END":
                # --- NEW: DO NOT PULL CORE BLOCKS INTO JSON ---
                if sub_label_name == "//patch104p-core-begin":
                    continue

                parts = stripped_line.split(':', 1)
                if len(parts) == 2:
                    lang_code, text = parts
                    lang_code = lang_code.strip()
                    text = text.strip()
                    if text.startswith('"') and text.endswith('"'):
                        text = text[1:-1]
                    text = apply_format_specifiers(text)

                    if lang_code in translations:
                        translations[lang_code][current_label] = text
                    else:
                        translations[lang_code] = {current_label: text}

            # 5. Identify the END of a block
            if stripped_line == "END":
                current_label = None
                current_context = "TODO"  # Reset context for the next block
                sub_label_name = ""       # Reset sub-label state

    return translations

def save_translations(translations, output_folder, exclude_langs=None):
    os.makedirs(output_folder, exist_ok=True)

    if exclude_langs is None:
        exclude_langs = []

    exclude_langs = [lang.lower() for lang in exclude_langs]

    for lang_code, data in translations.items():
        file_lang_code = lang_code
        if lang_code == 'US':
            file_lang_code = 'EN'
        elif lang_code == 'BP':
            file_lang_code = 'pt-BR'

        file_name_base = file_lang_code.lower()

        # Skip saving if this language is in the exclude list
        if file_name_base in exclude_langs:
            print(f"Skipping '{file_name_base}.json' (Excluded)")
            continue

        output_file = os.path.join(output_folder, f"{file_name_base}.json")
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Saved '{file_name_base}.json'")

def main(input_file, output_folder):
    # Define languages you want to exclude here
    langs_to_exclude = ['ctx']

    print("Parsing STR file...")
    translations = parse_file(input_file)

    print("Saving JSON files...")
    save_translations(translations, output_folder, exclude_langs=langs_to_exclude)
    print("Process complete!")

# Example usage:
file_path = r"generals.str"
output_folder = r"localization"

if __name__ == "__main__":
    main(file_path, output_folder)