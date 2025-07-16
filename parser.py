import re
import spacy
import nltk
from pdfminer.high_level import extract_text
from nltk.corpus import stopwords
import traceback
import random
import difflib


nltk.download("punkt")
nltk.download("stopwords")
nltk.download("averaged_perceptron_tagger")

nlp = spacy.load("en_core_web_sm")

def load_skills_database():
    try:
        with open("skills_db.txt", "r", encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ skills_db.txt not found. Falling back to default.")
        return [
            "python", "java", "sql", "excel", "communication", "leadership",
            "machine learning", "data analysis", "project management", "react", "node.js"
        ]

SKILL_DB = load_skills_database()



def extract_text_from_pdf(file):
    try:
        return extract_text(file)
    except Exception as e:
        print(f"PDF extraction failed: {e}")
        return ""

def extract_email(text):
    match = re.findall(r"[a-zA-Z0-9._%+]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match[0] if match else ""

def extract_phone(text):
    match = re.findall(r"\+?\d[\d\s\(\)\.]{8,}\d", text)
    return match[0] if match else ""

def extract_name(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    blacklist = {
        "java", "python", "sql", "resume", "intern", "developer", "project", "email", "contact",
        "android", "studio", "soft skills", "skills", "education", "experience", "throw", "bronze",
        "award", "runner", "winner", "badminton", "hockey", "cricket", "football"
    }

    # Heuristically check only the first 5–7 lines
    for line in lines[:7]:
        if any(char in line for char in ['•', '-', '·']) or any(c.isdigit() for c in line):
            continue

        clean_line = line.strip()
        words = clean_line.split()

        # Skip if line has too few/many words or contains blacklist keywords
        if 1 < len(words) <= 4:
            if not any(word.lower() in blacklist for word in words):
                if clean_line.replace(" ", "").isalpha():  # letters only
                    return clean_line.title()

    # Fallback to spaCy NER
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name_candidate = ent.text.strip()
            if all(word.lower() not in blacklist for word in name_candidate.split()):
                return name_candidate.title()

    return ""
def load_skills_database():
    with open("skills_db.txt", "r") as f:
        return [line.strip().lower() for line in f.readlines()]

SKILL_DB = load_skills_database()


def extract_skills(text):
    text = text.lower()
    tokens = re.findall(r'\b\w+(?:\.\w+)?\b', text)
    tokens = [t for t in tokens if t not in stopwords.words("english")]

    matched_skills = set()
    for token in tokens:
        close_matches = difflib.get_close_matches(token, SKILL_DB, n=1, cutoff=0.85)
        if close_matches:
            matched_skills.add(close_matches[0])

    return list(matched_skills)



def extract_education_summary(text):
    lines = text.split("\n")
    education_text = ""
    for i, line in enumerate(lines):
        lower = line.lower()
        if "vellore" in lower or "vit" in lower or "institute" in lower:
            institution = line.strip()
            course = ""
            cgpa = ""
            for j in range(i + 1, min(i + 4, len(lines))):
                next_line = lines[j].strip().lower()
                if any(keyword in next_line for keyword in ["b.tech", "m.tech", "b.e", "m.e", "computer science", "data science", "engineering"]):
                    course = lines[j].strip()
                if "cgpa" in next_line:
                    cgpa = lines[j].strip()
            education_text = f"{course} | {institution}"
            if cgpa:
                education_text += f" | {cgpa}"
            break
    return education_text

def extract_education_history(text):
    lines = text.split("\n")
    education_entries = []
    current_entry = ""
    course_or_score = ""
    year = ""
    for i, line in enumerate(lines):
        clean = line.strip()
        lower = clean.lower()
        if any(keyword in lower for keyword in ["school", "college", "university", "institute"]):
            if current_entry:
                entry = current_entry
                if course_or_score:
                    entry += f" | {course_or_score}"
                if year:
                    entry += f" | Year: {year}"
                education_entries.append(entry)
                course_or_score = ""
                year = ""
            current_entry = clean
        elif "cgpa" in lower or "percentage" in lower:
            course_or_score = clean
        elif re.search(r"\b20\d{2}\s*[-\u2013]\s*20\d{2}\b", clean):
            year_match = re.search(r"\b20\d{2}\s*[-\u2013]\s*20\d{2}\b", clean)
            if year_match:
                year = year_match.group()
    if current_entry:
        entry = current_entry
        if course_or_score:
            entry += f" | {course_or_score}"
        if year:
            entry += f" | Year: {year}"
        education_entries.append(entry)
    return education_entries

def extract_languages(text):
    lang_keywords = ["english", "tamil", "hindi"]
    return [lang.capitalize() for lang in lang_keywords if lang in text.lower()]

def extract_link(text, platform):
    # Case-insensitive match for full URLs
    pattern = rf"{platform}[:\-\s]*https?://[^\s\)\]]+"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0).split()[-1]

    # Fallback: raw URLs that include the platform name
    fallback = re.search(rf"https?://(?:www\.)?{platform.lower()}[^\s\)\]]+", text, re.IGNORECASE)
    return fallback.group(0) if fallback else ""


def extract_job_title(text):
    job_titles = ["intern", "software engineer", "developer", "data scientist", "analyst", "sde"]
    for title in job_titles:
        if title in text.lower():
            return title.title()
    return ""

def extract_expected_salary(text):
    match = re.findall(r"\b\d{2,3}[-]\d{2,3}k\b", text.lower())
    return match[0] if match else ""

def extract_age(text):
    age_match = re.search(r'\b[Aa]ge[:\s\-]+(\d{1,2})\b', text)
    if age_match:
        age = age_match.group(1)
        if 17 <= int(age) <= 60:
            return age
    return ""

def extract_location_details(text):
    city = ""
    country = ""
    full_address = ""
    lines = text.split("\n")
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in ["address", "location", "contact", "residence"]):
            city_match = re.search(r"\b(coimbatore|chennai|bangalore|mumbai|delhi|hyderabad|pune)\b", lower)
            if city_match:
                city = city_match.group(1).title()
        if "address" in lower:
            full_address = line.strip()
        if "india" in lower:
            country = "India"
    if not full_address and city and country:
        full_address = f"{city}, {country}"
    return city, country, full_address

def extract_years_of_exp(text):
    return "0-1" if re.search(r"\b(?:fresher|intern)\b", text, re.IGNORECASE) else ""

def parse_resume_from_path(file_path: str):
    try:
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            return {"error": "Could not extract text from the PDF."}

        # 🔍 Debug: print extracted resume text
        print("\n===== RESUME TEXT START =====\n")
        print(text)
        print("\n===== RESUME TEXT END =====\n")

        name = extract_name(text)
        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)
        education_list = extract_education_history(text)
        education_summary = extract_education_summary(text)
        languages = extract_languages(text)
        job_title = extract_job_title(text)
        expected_salary = extract_expected_salary(text)
        age = extract_age(text)
        years_of_exp = extract_years_of_exp(text)
        city, country, full_address = extract_location_details(text)
        print("Text:", text[:1000])  # Preview first 1000 chars
        print("Skills Extracted:", skills)
        socials = {
    "linkedin": extract_link(text, "linkedin"),
    "github": extract_link(text, "github"),
    "portfolio": extract_link(text, "portfolio")
}

 

        return {
            "name": name,
            "email": email,
            "profileImageURL": "",
            "profileDescription": job_title,
            "phone": phone,
            "age": age,
            "country": country,
            "city": city,
            "fullAddress": full_address,
            "jobTitle": job_title,
            "currentSalary": "",
            "expectedSalary": expected_salary,
            "education": education_summary,
            "yearsOfExp": years_of_exp,
            "languages": languages,
            "skills":skills,
            "categories": ["Software"] if any(skill in ["python", "java"] for skill in skills) else [],
            "allowProfileListing": True,
            "socials": {
                "linkedin": extract_link(text, "linkedin"),
                "github": extract_link(text, "github"),
                "portfolio": extract_link(text, "portfolio")
            },
            "socials":socials,
            "educationHistory": education_list,
            "workExperience": [],
            "awards": [],
            "CV": []
        }

    except Exception as e:
        print("Error in parse_resume:", traceback.format_exc())
        return {"error": f"An error occurred: {str(e)}"}

