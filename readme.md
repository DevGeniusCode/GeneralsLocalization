# C&C: Generals Localization Web Interface 🌍

This repository utilizes **Fink (by Inlang)** and a fully automated **GitHub Actions Pipeline** to provide a
streamlined, web-based workflow for translating and proofreading game strings for *Command & Conquer: Generals - Zero
Hour*.

## 🚀 Quick Start for Translators

You don't need to install any tools or clone the repository to contribute.

1. **Access the Editor:** Open
   the [Fink Project Link](https://fink.inlang.com/github.com/DevGeniusCode/GeneralsLocalization?project=%2Fproject.inlang&lang=en&lang=ctx&lang=ru).
2. **Sign In:** Authenticate with your GitHub account at the bottom of the page to enable editing.
3. **Select Your Language:** Use the language filter to find your target language (e.g., TR, UK, SR).
4. **Edit & Save:** Click on any string to modify the translation. Changes are synced directly via GitHub Pull Requests.

---

## ➕ How to Add a New Language

Adding a new language to the project is now fully automated. Choose the method that fits your situation:

### Method 1: Starting Fresh (Via Web Editor)

If you are translating a language from scratch:

1. Open the Fink Web Editor.
2. Add your language code via the project settings/UI.
3. The system will create a new `[lang].json` file. Once saved, our automated bot will register your language and
   prepare it for the game.

### Method 2: Importing a Legacy `.str` File

If you have an old community translation in `.str` format and want to port it to our modern web interface:

1. Fork this repository or create a new branch.
2. Place your `.str` file(s) into the `imports/[your-lang-code]/` directory (e.g., `imports/fr/generals.str`).
3. Open a Pull Request.
4. **Magic Happens:** Our automated bot will extract only your language strings, safely convert them to JSON, place them
   in the `localization/` folder, and automatically update all internal configuration scripts!

---

## 📖 Using Context (CTX: Strings)

To ensure the highest translation quality, it is **highly recommended** to use the **CTX** (Context/Comment) strings
alongside the English text:

* **What is CTX?:** The `CTX:` lines in the source file contain descriptions, developer notes, and explanations for each
  string.
* **Why use it?:** It clarifies whether a string is a button, a mission objective, a unit name, or a technical error
  message.
* **How to view:** In the web interface, ensure the `CTX` language/column is visible alongside `US` (English) and your
  target language.
* **Do not translate CTX:** These strings are for reference only and should not be modified.

---

## ⚠️ Important Guidelines

### 1. Maintain Format Specifiers (Strictly Enforced!)

Do not modify technical symbols like `\n` (new line) or specific variables like `{%d}` or `{%s}`. These are essential
for the game engine to render text correctly.
*🚨 **Note:** Our automated bot checks every translation. If a format specifier is missing or broken, your Pull Request
will fail and cannot be merged.*

### 2. Status & Approval

* **New Translations:** Feel free to fill in missing gaps.
* **Existing Text:** If you see an error in a "Verified" string, please leave a comment explaining the fix.
* **Approval:** All web edits will go through a final review by the project maintainers (@dmgreen, @xezon) before being
  merged.

### 3. Testing Your Changes (No Local Tools Required!)

You no longer need to download compilers or manipulate files locally.

1. When you make changes via Fink, a GitHub Pull Request is created.
2. Scroll to the bottom of your Pull Request page and click **Details** on the GitHub Actions check.
3. Go to the **Summary** tab and look for **Artifacts**.
4. Download which contains your language pack (e.g., `generals_EN.big`).
5. Place this `.big` file directly into your *C&C Generals Zero Hour* main installation directory to test your changes
   in-game!

---

## 📦 Releases & Downloads (For Players)

If you just want to download the latest completed translation packs to play the game:

1. Navigate to the [Releases](../../releases) section of this repository.
2. Download the `.big` file for your specific language (e.g., `!generals_PL.big`).
3. Place the file inside your game directory. The engine will load it automatically.

---

## ⚙️ Technical Workflow (For Developers & Maintainers)

The localization process uses a custom Python-based pipeline to bridge the gap between the legacy `.str` file and the
modern Inlang/Fink web editor.

### 🛡️ The "Core vs. Optional" Architecture (CRITICAL)

To avoid overwriting community-driven manual fixes, the synchronization scripts follow a strict **"Golden Rule"**:

* **`patch104p-core-begin` blocks:** These are strictly protected. The scripts will **ignore** these blocks entirely.
  They are neither exported to the JSON files nor overwritten by them. Core strings must be updated manually.
* **`patch104p-optional-begin` blocks (and standard blocks):** These are managed automatically. The web editor is the "
  master" for these strings.

### 🤖 The Automated CI/CD Pipeline (GitHub Actions)

Every time a translation is updated or a new language is added, our GitHub workflow (`build_pipeline.yml`) executes the
following steps automatically:

1. **Validation Gate (`validate_format.py`):** Ensures all format specifiers match the English source to prevent game
   crashes.
2. **Sync (`json2str.py`):** Merges all JSON files back into a master `generals.str` file, preserving Core blocks.
3. **Compile:** Uses `GameTextCompiler.exe` to convert the text into binary `.csf` files for every active language.
4. **Package:** Uses `GeneralsBigCreator.exe` to pack the `.csf` files into engine-ready `.big` archives.
5. **Distribute:** Uploads the `.big` files as PR Artifacts (for testing) or attaches them to Releases (upon merging to
   `main`).

---

## 🤝 Contributing

We are currently looking for native speakers to verify:

* **Ukrainian (UK)**
* **Turkish (TR)**
* **Serbian (SR)**
* **Azerbaijani**