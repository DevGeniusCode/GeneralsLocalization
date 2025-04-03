import os
import json
import re

# List of language codes we expect to encounter
# CO stands for 'context' and is used to store context data for each label if provided
language_codes = ['US', 'DE', 'FR', 'ES', 'IT', 'KO', 'ZH', 'BP', 'PL', 'RU', 'AR', 'UK', 'CO', 'HE']

# List of format specifiers
format_specifiers = [
    "%u", "%c", "%s", "%S", "%ls", "%hs", "%.0f%%", "%d", "%dms", "%d%%", "%d:0%d",
    "%d.%02d", "%d:%2.2d", "%d.%02d.%d", "%d:%02d:%02d", "\\n"
]

# Regular expression to match any of the format specifiers in the text
format_regex = re.compile(r'(' + '|'.join(map(re.escape, format_specifiers)) + r')')


def apply_format_specifiers(text):
    """ Apply curly braces around format specifiers in the text, including '&' with adjacent characters """
    # First, handle the '&' character that is followed by another character (e.g., &B, &O)
    text = re.sub(r'&(\w)', r'{&\1}', text)  # Match & followed by a word character and wrap in {}

    # Now handle the general format specifiers (like %d, %s, etc.)
    text = format_regex.sub(r'{\1}', text)

    return text


def parse_file(input_file):
    # Dictionary to store translations for each language
    translations = {lang: {} for lang in language_codes}
    # Dictionary to store context for the 'CO' language
    context_data = {}

    # Open the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        current_label = None
        current_context = "TODO"  # Default value for context

        # Iterate through each line in the file
        for line in file:
            # Remove the comment part (anything after //)
            if not line.startswith('// context:'):
                line = line.split('//')[0].strip()
            else:
                line = line.strip()

            if not line:  # Skip empty lines
                continue

            # If the line contains a label (e.g. GUI:GameOptions or similar)
            if ':' in line and not any(c in line for c in [' ', '"']):
                # This is a label
                current_label = line.strip()
                # Add context for this label in 'CO' if a context was set
                translations['CO'][current_label] = current_context
            elif current_label:
                # This is a translation line (e.g. US: "TEXT")
                parts = line.split(':', 1)
                if len(parts) == 2:
                    lang_code, text = parts
                    lang_code = lang_code.strip()
                    text = text.strip().strip('"')  # Remove quotes around the text

                    # Apply the format specifier transformation
                    text = apply_format_specifiers(text)

                    # If the language code is in our list, add the translation
                    if lang_code in translations:
                        translations[lang_code][current_label] = text
                    else:
                        # If the language code is not recognized, we set the translation as "TODO"
                        translations[lang_code][current_label] = ""

            # If we encounter the "END" keyword, reset current_label and context
            if line.strip() == "END":
                current_label = None
                current_context = "TODO"  # Reset context after each block

            # If the line contains a context (e.g. // context: Button to go to the game options screen)
            elif line.startswith("// context:"):
                current_context = line.split(":", 1)[1].strip()

    return translations


def save_translations(translations, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save each language's translations to its respective JSON file
    for lang_code, data in translations.items():
        if lang_code == 'US':
            lang_code = 'EN'
        elif lang_code == 'BP':
            lang_code = 'pt-BR'
        output_file = os.path.join(output_folder, f"{lang_code.lower()}.json")
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)


def main(input_file, output_folder):
    # Parse the input file to get the translations
    translations = parse_file(input_file)

    # Save the parsed translations to individual language JSON files
    save_translations(translations, output_folder)


# Example usage:
file_path = r"generals.str"
output_folder = r"localization"
main(file_path, output_folder)
