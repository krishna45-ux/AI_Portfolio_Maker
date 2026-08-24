# AI-Assisted Resume Portfolio Generator

## 📌 Project Overview
The **AI-Assisted Resume Portfolio Generator** is an automated Python tool designed to take a raw, unstructured text resume and instantly convert it into a fully styled, professional HTML portfolio website. 

Instead of dealing with complex UI builders or writing HTML manually, this tool leverages the power of Large Language Models (specifically Google's Gemini API) to understand the semantic meaning of your resume, extract key details (like experience, education, projects, and skills) into a strict structured format (JSON), and dynamically inject that data into a clean HTML/CSS template.

---

## ✨ Key Features
- **Intelligent Parsing**: Understands plain text resumes, regardless of how they are formatted or spaced, using the Gemini generative AI model.
- **Strict Data Extraction**: Employs advanced prompt engineering to ensure the AI acts *only* as a data extractor. It does not invent, hallucinate, or pad your resume with fake information.
- **Dynamic Templating**: Uses native Python string manipulation to populate the HTML. If your resume lacks a certain section (like "Projects" or "Certifications"), that section is intelligently omitted from the final website to prevent empty white space.
- **Zero Heavy Frameworks**: Built using only standard Python libraries and basic HTML5/CSS3. No React, Vue, Jinja2, or heavy node modules required.
- **Robust Error Handling**: Safely catches missing files, empty resumes, API connection timeouts, and malformed JSON responses without crashing.

---

## 📂 Project File Structure
Here is a breakdown of what each file in this repository does:

- `main.py`: The core Python script that handles reading the text, communicating with the Gemini API, parsing the JSON, and writing the final HTML file.
- `template.html`: The base HTML5 structure. It contains `{PLACEHOLDER}` tokens that the Python script looks for and replaces with your actual data.
- `style.css`: A custom, responsive CSS file that ensures the generated portfolio looks modern, clean, and professional on both desktop and mobile devices.
- `resume.txt`: The input file. You paste your raw resume text here.
- `.env.example`: A template for environment variables. You rename this to `.env` and put your private API key inside.
- `.gitignore`: Ensures that sensitive files (like your `.env` containing your API key) and generated output files are not accidentally uploaded to GitHub.
- `requirements.txt`: A simple list of the Python packages required to run this project (`google-genai` / `google-generativeai` and `python-dotenv`).

---

## ⚙️ Detailed Workflow (How it Works Under the Hood)

### 1. Input Reading & Validation
When you execute `main.py`, the script first looks for `resume.txt`. It reads the content and performs a basic sanitization pass—stripping out massive blocks of empty lines and trailing spaces. 
*Validation*: If the file is missing, completely empty, or contains fewer than 50 characters (meaning it's too short to be a real resume), the script safely aborts and alerts the user.

### 2. Prompt Engineering & API Call
The script uses the `python-dotenv` library to securely load your Gemini API key from the `.env` file. It then constructs a highly specific prompt for the Gemini AI. 
The prompt is designed with strict boundaries:
- It defines the exact JSON schema the AI must use.
- It explicitly forbids the AI from wrapping the output in markdown code blocks.
- It commands the AI to use `""` (empty strings) or `[]` (empty lists) if information is missing.
- It explicitly forbids the AI from hallucinating or inferring details not explicitly written in `resume.txt`.

### 3. JSON Parsing & Safety
Once Gemini returns the data, the script attempts to parse it using Python's native `json` library. 
*Safety Net*: LLMs can sometimes be unpredictable. If the AI happens to return invalid JSON (e.g., a missing comma or conversational text), the script catches the `json.JSONDecodeError`, prints the raw output for debugging, and shuts down safely instead of failing during the HTML generation phase.

### 4. HTML Generation
The script opens `template.html` as a raw string. It then uses Python's `.replace()` method to swap out placeholder tags (like `{NAME}` or `{HEADLINE}`) with the data extracted from the JSON.
For lists (like Skills, Experience, or Education), the script iterates through the JSON arrays, wraps the data in the appropriate HTML tags (like `<li>` or `<div>`), and injects them into the template. If an array is empty, the script replaces the section's placeholder with an empty string, completely erasing that section from the final website.
Finally, the populated string is saved to your hard drive as `portfolio.html`.

---

## 💻 How to Run
Once setup is complete, simply run the Python script from your terminal:
```bash
python main.py
```
If everything is successful, you will see a success message in your terminal, and a new file named `portfolio.html` will appear in your folder. Double-click it to view your new website in your browser!

---

## 🧪 Testing Results
This script has been rigorously tested against edge cases to ensure stability:
- **Missing `resume.txt`**: Handled safely; script exits with a helpful "file not found" message.
- **Empty or Very Short Resume**: Script calculates character length and rejects resumes under 50 characters.
- **Valid Resume**: Safely parses and generates `portfolio.html`.
- **Missing Sections**: Handled cleanly. If a user has no "Projects", the Projects section is entirely removed from the HTML rather than displaying an empty box.
- **Missing API Key**: Handled securely. If the `.env` file is missing or the key is blank, the script warns the user and exits.
- **API Failure / Timeout**: Wrapped in try/except blocks to ensure the program fails gracefully with an error readout rather than a messy stack trace.

---

## ⚠️ Limitations & AI Risks
- **Hallucinations**: While the prompt explicitly forbids making up information, Large Language Models are inherently probabilistic. There is always a tiny risk that the AI might rephrase a bullet point or alter a date slightly. **You must always proofread your generated `portfolio.html` before sharing it publicly.**
- **Formatting Constraints**: The script is designed to fill a specific HTML layout. If your resume has incredibly complex nested structures (like multiple sub-roles under a single company spanning different overlapping dates), the AI will flatten it to fit the provided JSON schema.

---

## 🤖 AI Usage Log
*(As required by the project brief)*
- **AI Tool Used**: Gemini 3.6 Flash / Antigravity AI Assistant
- **Prompt/Request**: "Act as an expert Python developer. Write a Python script..."
- **What the tool generated**: The initial codebase structure including Python logic, HTML boilerplate, CSS styling, environment configs, and dependency lists.
- **Modifications Made**: 
  - Updated the API model endpoint to the latest supported standard (`gemini-3.6-flash`).
  - Implemented specific length validation for `resume.txt` to satisfy mandatory testing constraints.
  - Added this comprehensive `README.md` and a secure `.gitignore`.
