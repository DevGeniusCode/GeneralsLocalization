import os
import json
import re

# Exact list of format specifiers from your source
format_specifiers = [
    "%u", "%c", "%s", "%S", "%ls", "%hs", "%.0f%%", "%d", "%dms", "%d%%", "%d:0%d",
    "%d.%02d", "%d:%2.2d", "%d.%02d.%d", "%d:%02d:%02d", "\\n"
]

# Supported language prefixes in the .str file
language_prefixes = [f"{lang}:" for lang in
                     ['US', 'DE', 'FR', 'ES', 'IT', 'KO', 'ZH', 'BP', 'PL', 'RU', 'AR', 'UK', 'SV', 'HE']]


def remove_format_specifiers(text):
    """ Revert the curly braces around format specifiers """
    if not isinstance(text, str):
        return ""

    text = re.sub(r'\{&(\w)\}', r'&\1', text)
    escaped_specifiers = [re.escape(f"{{{s}}}") for s in format_specifiers]
    format_regex = re.compile(r'(' + '|'.join(escaped_specifiers) + r')')

    def strip_braces(match):
        return match.group(0)[1:-1]

    return format_regex.sub(strip_braces, text)


def load_all_jsons(input_folder, exclude_langs=None):
    """ Reads JSON files and builds a dictionary of translations, skipping excluded languages """
    if exclude_langs is None:
        exclude_langs = []

    # Convert exclude list to lowercase for easy matching
    exclude_langs = [lang.lower() for lang in exclude_langs]

    translations = {}

    # Map JSON filenames to their respective .str prefixes
    file_to_lang = {
        'en': 'US:', 'us': 'US:',
        'pt-br': 'BP:', 'bp': 'BP:',
        'de': 'DE:', 'fr': 'FR:', 'es': 'ES:', 'it': 'IT:',
        'ko': 'KO:', 'zh': 'ZH:', 'pl': 'PL:', 'ru': 'RU:',
        'ar': 'AR:', 'uk': 'UK:', 'se': 'SV:', 'he': 'HE:'
    }

    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' not found.")
        return translations

    for filename in os.listdir(input_folder):
        if not filename.endswith('.json'):
            continue

        lang_key = filename[:-5].lower()  # Remove .json extension

        # Check if this language is in the exclude list
        if lang_key in exclude_langs:
            print(f"Skipping '{filename}' (Excluded)")
            continue

        # Ignore files that are not mapped languages (e.g., co.json)
        if lang_key not in file_to_lang:
            continue

        lang_prefix = file_to_lang[lang_key]
        file_path = os.path.join(input_folder, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                for label, text in data.items():
                    if text is not None and text != "":
                        clean_text = remove_format_specifiers(text)

                        if label not in translations:
                            translations[label] = {}
                        translations[label][lang_prefix] = clean_text
        except Exception as e:
            print(f"Error loading {filename}: {e}")

    return translations


def update_str_file(statusquo_file, output_file, translations):
    """ Reads the source file and replaces lines if a new translation exists """
    if not os.path.exists(statusquo_file):
        print(f"Error: Source file '{statusquo_file}' not found.")
        return

    with open(statusquo_file, mode="r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    is_in_label_block = False
    current_label = ""
    sub_label_name = ""  # <-- NEW: Tracks core/optional blocks

    for line in lines:
        stripped_line = line.strip()

        # Ignore empty lines or comments
        if not stripped_line or stripped_line.startswith("//"):
            # Track core/optional blocks
            if "patch104p-core-begin" in stripped_line or "patch104p-optional-begin" in stripped_line:
                sub_label_name = stripped_line
            elif "patch104p-core-end" in stripped_line or "patch104p-optional-end" in stripped_line:
                sub_label_name = ""

            new_lines.append(line)
            continue

        if not is_in_label_block:
            if not stripped_line.lower().startswith("end") and ":" in stripped_line:
                # Entered a new label block
                is_in_label_block = True
                current_label = stripped_line
            new_lines.append(line)

        elif stripped_line.lower().startswith("end"):
            # Exited a label block
            is_in_label_block = False
            sub_label_name = ""
            new_lines.append(line)

        else:
            # --- NEW: DO NOT OVERWRITE CORE BLOCKS ---
            if sub_label_name == "//patch104p-core-begin":
                new_lines.append(line)
                continue

            # Inside an optional or normal label block, check if it's a language line
            updated_line = line
            for prefix in language_prefixes:
                if stripped_line.startswith(prefix):
                    # Found a language prefix. Check if we have a new translation for it
                    if current_label in translations and prefix in translations[current_label]:
                        new_text = translations[current_label][prefix]

                        # Fix for quotes: ensure inner quotes are properly escaped
                        safe_text = new_text.replace('\\"', '"').replace('"', '\\"')

                        # Preserve original indentation
                        leading_spaces = line[:len(line) - len(line.lstrip())]
                        updated_line = f'{leading_spaces}{prefix} "{safe_text}"\n'
                    break  # No need to check other prefixes for this line

            new_lines.append(updated_line)

    # Write the new file
    with open(output_file, mode="w", encoding="utf-8") as f:
        f.writelines(new_lines)


def main():
    # Define languages you DO NOT want to inject into the STR file
    # Example: langs_to_exclude = ['he', 'fr']
    langs_to_exclude = ['ctx']

    input_folder = "localization"
    statusquo_file = "generals.str"  # Your master file
    output_file = "generals.str"  # Overwriting the same file

    print("1. Loading JSON data from localization folder...")
    translations = load_all_jsons(input_folder, exclude_langs=langs_to_exclude)
    print(f"   Loaded translations for {len(translations)} labels.")

    print(f"2. Updating the STR file ({statusquo_file})...")
    update_str_file(statusquo_file, output_file, translations)
    print(f"--- Process completed successfully! Saved to '{output_file}' ---")


if __name__ == "__main__":
    main()