# Resume Parser (FastAPI)

This project parses resumes (PDF) using FastAPI and extracts structured data like name, email, skills, education, and more. Parsed data is stored in an SQLite database and rendered through HTML templates.

## 🔧 Tech Stack
- FastAPI
- SQLModel (SQLite)
- PDFMiner, spaCy, NLTK
- Jinja2 Templates

## 🚀 Features
- Upload resumes in PDF format
- Extracts:
  - Name, Email, Phone, Address
  - Skills, Languages, Education
  - Job Title, Salary Expectation
  - Social Links (LinkedIn, GitHub)
- Stores parsed results in SQLite
- View parsed resumes at `/resumes`

## 🛠️ How to Run

```bash
uvicorn main:app --reload
