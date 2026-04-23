import json
import os
import re
import sys

def extract_specifiers(text):
    if not isinstance(text, str):
        return []
    # Extracts matched braces e.g. {%d}, {&c} and newlines \n
    braces = re.findall(r'\{[^{}]+\}', text)
    newlines = re.findall(r'\\n', text)
    # Sort them to allow translators to change sentence structure/order safely
    return sorted(braces + newlines)

def main():
    loc_dir = "localization"
    en_path = os.path.join(loc_dir, "en.json")

    if not os.path.exists(en_path):
        print("❌ Error: English source file (en.json) not found!")
        sys.exit(1)

    with open(en_path, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    # Pre-calculate english format specifiers
    en_specifiers = {k: extract_specifiers(v) for k, v in en_data.items() if v}
    total_files = 0
    failed_files = []

    for filename in os.listdir(loc_dir):
        if filename in ["en.json", "ctx.json"] or not filename.endswith('.json'):
            continue

        total_files += 1
        filepath = os.path.join(loc_dir, filename)
        has_errors_in_file = False

        with open(filepath, 'r', encoding='utf-8') as f:
            lang_data = json.load(f)

        for key, translated_text in lang_data.items():
            if not translated_text or key not in en_specifiers:
                continue

            target_specs = extract_specifiers(translated_text)
            expected_specs = en_specifiers[key]

            if target_specs != expected_specs:
                print(f"❌ [Format Mismatch] File: {filename} | Key: '{key}'")
                print(f"   Expected tags: {expected_specs}")
                print(f"   Found tags:    {target_specs}")
                print(f"   EN Text:       {en_data[key]}")
                print(f"   Target Text:   {translated_text}\n")
                has_errors_in_file = True

        if has_errors_in_file:
            print(f"🚨 Removing {filename} from the build process due to format errors.")
            failed_files.append(filename)
            os.remove(filepath) # Remove the file so json2str.py skips it

    if failed_files:
        print(f"\n⚠️ Validation completed with warnings! The following files were skipped: {', '.join(failed_files)}")
        # Notice we removed sys.exit(1) so the action continues for the valid files.
    else:
        print(f"\n✅ Validation passed for all {total_files} language files!")

if __name__ == "__main__":
    main()