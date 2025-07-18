# 🧠 AI Resume Parser (FastAPI)

A FastAPI-based application to intelligently parse PDF resumes and extract structured data like contact info, skills, education, experience, and social links. Parsed data is stored in a database and resumes are backed up to Cloudinary using the user's IP as the filename.

---

## 🔧 Tech Stack

- 🏃 FastAPI – High-performance Python web framework
- 🗃️ SQLModel + SQLite – Lightweight, modern ORM
- 🧠 NLP – spaCy, NLTK for language understanding
- 📄 PDF Parsing – PDFMiner
- 🎨 Jinja2 Templates + Bootstrap for UI
- ☁️ Cloudinary for file storage

---

## 🚀 Features

✅ Upload resumes in PDF format  
✅ Parse the following from the document:
- Name, Email, Phone
- Address (City, Country, Full Address)
- Skills & Languages
- Education & Education History
- Job Title, Age, Years of Experience
- Expected Salary
- Socials: LinkedIn, GitHub, Portfolio

✅ Save resume PDF to Cloudinary using client IP as part of filename  
✅ View all parsed resumes at `/resumes`  
✅ Download parsed summary PDF  
✅ View or download original PDF from Cloudinary

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/ai-resume-parser.git
cd ai-resume-parser
