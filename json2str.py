import os
import json
import re

# List of language codes in the order they should ideally appear
language_codes = ['US', 'DE', 'FR', 'ES', 'IT', 'KO', 'ZH', 'BP', 'PL', 'RU', 'AR', 'UK', 'CTX', 'HE']

# Exact same list of format specifiers from the original code
format_specifiers = [
    "%u", "%c", "%s", "%S", "%ls", "%hs", "%.0f%%", "%d", "%dms", "%d%%", "%d:0%d",
    "%d.%02d", "%d:%2.2d", "%d.%02d.%d", "%d:%02d:%02d", "\\n"
]


def remove_format_specifiers(text):
    """ Revert the curly braces around format specifiers """
    # Revert the '&' character mapping (e.g., {&B} -> &B)
    text = re.sub(r'{&(\w)}', r'&\1', text)

    # Revert the general format specifiers (e.g., {%d} -> %d)
    for spec in format_specifiers:
        text = text.replace(f"{{{spec}}}", spec)

    return text


def load_translations(input_folder):
    # Dictionary to store all loaded data
    translations = {lang: {} for lang in language_codes}

    # Reverse mapping for the special cases
    file_to_lang = {
        'en': 'US',
        'pt-br': 'BP'
    }

    # Add regular mappings (e.g., 'de' -> 'DE')
    for lang in language_codes:
        if lang not in ['US', 'BP']:
            file_to_lang[lang.lower()] = lang

    # Read all JSON files in the folder
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' not found.")
        return translations

    for filename in os.listdir(input_folder):
        if not filename.endswith('.json'):
            continue

        lang_key = filename[:-5].lower()  # remove '.json'

        if lang_key in file_to_lang:
            original_lang_code = file_to_lang[lang_key]
            file_path = os.path.join(input_folder, filename)

            with open(file_path, 'r', encoding='utf-8') as json_file:
                translations[original_lang_code] = json.load(json_file)

    return translations


def save_str_file(translations, output_file):
    # We use 'CTX' (Context) keys to preserve the original order of the labels
    all_labels = list(translations.get('CTX', {}).keys())

    # In case there are labels that somehow don't exist in 'CO', add them at the end
    for lang, data in translations.items():
        if lang == 'CTX':
            continue
        for label in data.keys():
            if label not in all_labels:
                all_labels.append(label)

    # Write out the .str file
    with open(output_file, 'w', encoding='utf-8') as file:
        for label in all_labels:
            # 1. Write the Context if it exists and isn't "TODO"
            context = translations['CTX'].get(label, "TODO")
            if context and context != "TODO":
                file.write(f"// context: {context}\n")

            # 2. Write the Label itself
            file.write(f"{label}\n")

            # 3. Write each translation for this label
            for lang in language_codes:
                if lang == 'CTX':
                    continue  # CO is handled above

                if label in translations[lang]:
                    raw_text = translations[lang][label]

                    # Only write if it's not an empty placeholder
                    # (In your original code missing langs were set to "", you can adjust this logic if needed)
                    if raw_text != "":
                        # Revert the {} wrappers
                        reverted_text = remove_format_specifiers(raw_text)
                        # Write in the Lang: "Text" format
                        file.write(f"  {lang}: \"{reverted_text}\"\n")

            # 4. End the block
            file.write("END\n\n")


def main(input_folder, output_file):
    # Load JSONs back into memory
    translations = load_translations(input_folder)

    # Save back to a .str file
    save_str_file(translations, output_file)
    print(f"Successfully generated: {output_file}")


# Example usage:
input_folder = r"localization"
output_file = r"generals.str"
main(input_folder, output_file)