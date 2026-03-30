# C&C: Generals Localization Web Interface 🌍

This repository utilizes **Fink (by Inlang)** to provide a streamlined, web-based workflow for translating and proofreading game strings for *Command & Conquer: Generals - Zero Hour*.

## 🚀 Quick Start for Translators

You don't need to install any tools or clone the repository to contribute.

1. **Access the Editor:** Open the [Fink Project Link](https://fink.inlang.com/github.com/DevGeniusCode/GeneralsLocalization?project=%2Fproject.inlang&lang=en&lang=ctx&lang=ru).
2. **Sign In:** Authenticate with your GitHub account at the bottom of the page to enable editing.
3. **Select Your Language:** Use the language filter to find your target language (e.g., TR, UK, SR).
4. **Edit & Save:** Click on any string to modify the translation. Changes are synced directly via GitHub Pull Requests.

---

## 📖 Using Context (CTX: Strings)

To ensure the highest translation quality, it is **highly recommended** to use the **CTX** (Context/Comment) strings alongside the English text:

* **What is CTX?:** The `CTX:` lines in the source file contain descriptions, developer notes, and explanations for each string.
* **Why use it?:** It clarifies whether a string is a button, a mission objective, a unit name, or a technical error message.
* **How to view:** In the web interface, ensure the `CTX` language/column is visible alongside `US` (English) and your target language. 
* **Do not translate CTX:** These strings are for reference only and should not be modified.

---

## 🛠️ Key Features

* **Browser-Based Editing:** No need for `.str` or `.csf` compilers locally.
* **Direct GitHub Integration:** Every edit can be submitted as a contribution to the main project.
* **Format Specifier Support:** Handles special game characters and line breaks properly.

---

## ⚠️ Important Guidelines

### 1. Maintain Format Specifiers
Do not modify technical symbols like `\n` (new line) or specific variables. These are essential for the game engine to render text correctly.

### 2. Status & Approval
* **New Translations:** Feel free to fill in missing gaps.
* **Existing Text:** If you see an error in a "Verified" string, please leave a comment explaining the fix.
* **Approval:** All web edits will go through a final review by the project maintainers (@dmgreen, @xezon) before being merged.

### 3. Testing Your Changes
If you wish to test your translations in-game:
1. Export the updated `.str` file.
2. Use the **GameTextCompiler** to generate a `generals.csf`.
3. Place the file in: `\Data\English\generals.csf`.

---

## ⚙️ Technical Workflow (For Developers & Maintainers)

The localization process uses a custom Python-based pipeline to bridge the gap between the legacy `.str` file and the modern Inlang/Fink web editor. 

### 🛡️ The "Core vs. Optional" Architecture (CRITICAL)
To avoid overwriting community-driven manual fixes, the synchronization scripts follow a strict **"Golden Rule"**:
* **`patch104p-core-begin` blocks:** These are strictly protected. The scripts will **ignore** these blocks entirely. They are neither exported to the JSON files nor overwritten by them. Core strings must be updated manually.
* **`patch104p-optional-begin` blocks (and standard blocks):** These are managed automatically. The web editor is the "master" for these strings.

### 1. Extracting to Web: `str2json.py`
This script parses the master `generals.str` file and generates individual JSON files (e.g., `en.json`, `tr.json`, `ctx.json`) inside the `localization/` folder for the web editor to read.

* **Format Specifiers Protection:** To prevent accidental deletion of game variables during translation, the script automatically wraps format specifiers (like `%d`, `%s`, `\n`) and UI hotkeys (like `&B`) in **curly braces** `{}`. 
    * *Example:* `&Build` becomes `{&B}uild`.
    * *Example:* `Score: %d` becomes `Score: {%d}`.
* **Context Injection:** Extracts comments marked with `// context:` and maps them to the `ctx.json` file.
* **Usage:** Simply run `python str2json.py`. You can exclude specific languages from being exported by modifying the `langs_to_exclude` list inside the script.

### 2. Injecting from Web: `json2str.py`
Once translations are updated in the web interface and synced to the repository, this script pulls the data from the `localization/*.json` files and injects it back into the master `generals.str` file.

* **Safe Injection:** It reads the existing `generals.str` to preserve all original indentation, comments, and structure.
* **Format Restoration:** It safely removes the protective `{}` braces from format specifiers.
* **Usage:** Run `python json2str.py`. It will update the `generals.str` in place, skipping any blocks marked as *Core*.

### 3. Final Compilation
After running `json2str.py`, the finalized `generals.str` must be compiled into a `.csf` file using the GameTextCompiler for use in-game.

---

## 🤝 Contributing
We are currently looking for native speakers to verify:
* **Ukrainian (UK)**
* **Hebrew (IL)**
* **Turkish (TR)**
* **Serbian (SR)**
* **Azerbaijani**