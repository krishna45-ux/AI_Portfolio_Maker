import os
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

client = None

def load_environment():
    """Load and verify environment variables."""
    global client
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("Error: GEMINI_API_KEY not found or not set in .env file.")
        exit(1)
    client = genai.Client(api_key=api_key)

def read_resume(filepath):
    """Read and clean resume text."""
    if not os.path.exists(filepath):
        print(f"Error: Could not find '{filepath}'. Please create this file and add your resume text.")
        exit(1)
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        if not text.strip():
            print(f"Error: The file '{filepath}' is empty.")
            exit(1)
            
        # Clean text: remove extra blank lines and trailing spaces
        cleaned_text = re.sub(r'\n\s*\n', '\n\n', text).strip()
        
        if len(cleaned_text) < 50:
            print(f"Error: The file '{filepath}' is too short to be a valid resume.")
            exit(1)
            
        return cleaned_text
    except Exception as e:
        print(f"Error reading '{filepath}': {e}")
        exit(1)

def extract_json_with_gemini(resume_text):
    """Call Gemini API to extract structured JSON from resume text."""
    print("Calling Gemini API to parse resume...")
    try:
        prompt = f"""You are a precise data extraction tool.
Your task is to read the provided resume text and extract the information into a strict JSON format.

RULES:
1. Rely strictly on the provided resume text. Do not invent, hallucinate, or infer any skills, dates, companies, or links not present in the text.
2. Output ONLY a raw, valid JSON object. 
3. DO NOT wrap the output in Markdown blocks (e.g., no ```json ... ```).
4. DO NOT include any conversational text, explanations, or preambles.
5. Provide empty strings "" or empty lists [] for any missing information.
6. Keep the Professional Summary concise and factual.

REQUIRED JSON STRUCTURE:
{{
    "Name": "",
    "Headline": "",
    "Professional Summary": "",
    "Skills": [],
    "Education": [
        {{
            "Institution": "",
            "Degree": "",
            "Dates": "",
            "Details": ""
        }}
    ],
    "Experience": [
        {{
            "Company": "",
            "Title": "",
            "Dates": "",
            "Responsibilities": []
        }}
    ],
    "Projects": [
        {{
            "Name": "",
            "Description": "",
            "Link": ""
        }}
    ],
    "Achievements": [],
    "Contact": {{
        "Email": "",
        "Phone": "",
        "LinkedIn": "",
        "GitHub": "",
        "Website": ""
    }}
}}

RESUME TEXT:
{resume_text}
"""
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        # Attempt to clean potential markdown formatting if Gemini still adds it despite instructions
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        if result_text.startswith("```"):
            result_text = result_text[3:]
            
        return result_text.strip()
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        exit(1)

def parse_json(json_string):
    """Safely parse the returned JSON string."""
    try:
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON returned by Gemini API. It might not be valid JSON.\nDetails: {e}")
        print(f"Raw API Output:\n{json_string}")
        exit(1)

def generate_html(data, template_path, output_path):
    """Inject JSON data into HTML template and save."""
    print("Generating HTML portfolio...")
    if not os.path.exists(template_path):
        print(f"Error: Could not find template file '{template_path}'.")
        exit(1)
        
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
            
        # 1. Basic Text Fields
        template = template.replace("{NAME}", data.get("Name", "") or "My Portfolio")
        template = template.replace("{HEADLINE}", data.get("Headline", ""))
        
        # 2. Contact Info (Generates links automatically if it's a URL or email)
        contact_html = []
        for key, val in data.get("Contact", {}).items():
            if not val: continue
            if key.lower() == "email":
                contact_html.append(f'<a href="mailto:{val}">{val}</a>')
            elif key.lower() in ["linkedin", "github", "website"] and val.startswith("http"):
                contact_html.append(f'<a href="{val}" target="_blank">{key}</a>')
            else:
                contact_html.append(f'<span>{val}</span>')
        template = template.replace("{CONTACT_INFO}", " | ".join(contact_html))

        # 3. Simple List Sections (Skills, Achievements)
        def build_list(title, items, cls):
            """Helper to quickly build simple <ul> lists."""
            if not items: return ""
            return f"<section><h2>{title}</h2><ul class='{cls}'>{''.join(f'<li>{i}</li>' for i in items)}</ul></section>"
            
        summary = data.get("Professional Summary", "")
        template = template.replace("{SUMMARY_SECTION}", f"<section><h2>Professional Summary</h2><p>{summary}</p></section>" if summary else "")
        template = template.replace("{SKILLS_SECTION}", build_list("Skills", data.get("Skills", []), "skills-list"))
        template = template.replace("{ACHIEVEMENTS_SECTION}", build_list("Achievements & Certifications", data.get("Achievements", []), "achievements-list"))

        # 4. Complex Repeating Sections (Experience, Projects, Education)
        def build_section(title, items, formatter):
            """Helper to build complex sections using a provided string formatter lambda."""
            if not items: return ""
            return f"<section><h2>{title}</h2>{''.join(formatter(i) for i in items)}</section>"
            
        # We use concise lambda functions with f-strings to format each item in the lists!
        exp_fmt = lambda x: f"<div class='experience-item'><div class='item-header'><span class='item-title'>{x.get('Title', '')}</span><span class='item-date'>{x.get('Dates', '')}</span></div><div class='item-subtitle'>{x.get('Company', '')}</div><ul class='task-list'>{''.join(f'<li>{r}</li>' for r in x.get('Responsibilities', []))}</ul></div>"
        template = template.replace("{EXPERIENCE_SECTION}", build_section("Experience", data.get("Experience", []), exp_fmt))

        proj_fmt = lambda x: f"<div class='project-item'><div class='item-header'><a href='{x.get('Link', '#')}' target='_blank' class='item-title'>{x.get('Name', '')}</a></div><p>{x.get('Description', '')}</p></div>" if str(x.get('Link', '')).startswith('http') else f"<div class='project-item'><div class='item-header'><span class='item-title'>{x.get('Name', '')}</span></div><p>{x.get('Description', '')}</p></div>"
        template = template.replace("{PROJECTS_SECTION}", build_section("Projects", data.get("Projects", []), proj_fmt))

        edu_fmt = lambda x: f"<div class='education-item'><div class='item-header'><span class='item-title'>{x.get('Degree', '')}</span><span class='item-date'>{x.get('Dates', '')}</span></div><div class='item-subtitle'>{x.get('Institution', '')}</div><p>{x.get('Details', '')}</p></div>"
        template = template.replace("{EDUCATION_SECTION}", build_section("Education", data.get("Education", []), edu_fmt))

        # 5. Save Output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"Success! Portfolio saved to {output_path}")

    except Exception as e:
        print(f"Error generating HTML: {e}")
        exit(1)

def main():
    load_environment()
    
    resume_file = "resume.txt"
    template_file = "template.html"
    output_file = "portfolio.html"
    
    # 1. Read and clean resume
    resume_text = read_resume(resume_file)
    
    # 2. Extract JSON using Gemini
    json_string = extract_json_with_gemini(resume_text)
    
    # 3. Parse JSON
    resume_data = parse_json(json_string)
    
    # 4. Generate HTML
    generate_html(resume_data, template_file, output_file)

if __name__ == "__main__":
    main()
