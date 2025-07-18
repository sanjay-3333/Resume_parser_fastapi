An AI-powered resume parser built with FastAPI, Bootstrap, and Cloudinary for file storage, supporting structured resume extraction and PDF export.

🚀 Features
✔ Upload & Parse Resumes (PDF)
✔ AI-driven Resume Data Extraction
✔ Cloud Storage Integration (Cloudinary)
✔ IP-based Resume Naming for Uniqueness
✔ Responsive Bootstrap UI (Corporate Design)
✔ View Resumes in Dashboard with Pagination & Search
✔ Detailed View in Modal (AJAX)
✔ Download Parsed Resume as PDF
✔ SQLite Database with SQLModel ORM
✔ Secure via Environment Variables (.env)

🛠 Tech Stack
Backend: FastAPI, SQLModel

Frontend: HTML, Bootstrap 5, Jinja2

Database: SQLite

Cloud Storage: Cloudinary

PDF Generation: FPDF

Others: dotenv, mimetypes

📂 Project Structure
bash
Copy
Edit
resume_parser_fastapi/
│
├── main.py                 # FastAPI backend logic
├── models.py               # SQLModel database models
├── parser.py               # Resume parsing logic
├── templates/
│   ├── index.html          # Home page
│   ├── resumes.html        # Uploaded resumes page
├── static/
│   ├── bootstrap.min.css
│   ├── bootstrap.bundle.min.js
│   └── favicon.ico
├── uploads/                # Temporary uploads
├── resumes.db              # SQLite DB
├── output_resume.pdf       # Generated PDF
└── .env                    #Environment variables



⚙️ Setup Instructions
1. Clone Repository
bash
Copy
Edit
git clone https://github.com/sanjay-3333/Resume_parser_fastapi.git
cd Resume_parser_fastapi


2. Create Virtual Environment & Install Dependencies
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt


3. Configure Environment Variables
Create a .env file:

ini
Copy
Edit
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret


4. Run the Application
bash
Copy
Edit
uvicorn main:app --reload
Visit: http://127.0.0.1:8000

📌 Usage
Upload Resume: Extracts structured details (Name, Email, Skills, etc.)

View All Resumes: Paginated, searchable dashboard

View Details: Modal with full resume data

Download Parsed Resume: PDF with extracted info

🔗 Links
Cloudinary Docs:https://cloudinary.com/documentation

FastAPI Docs:https://fastapi.tiangolo.com/