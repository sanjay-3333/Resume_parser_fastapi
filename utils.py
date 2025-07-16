from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(data, file_path="parsed_resume.pdf"):
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Parsed Resume Summary")
    y -= 40

    c.setFont("Helvetica", 12)

    def write_line(label, value):
        nonlocal y
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, f"{label}: {value}")
        y -= 20

    fields = [
        ("Name", data.get("name", "")),
        ("Email", data.get("email", "")),
        ("Phone", data.get("phone", "")),
        ("Job Title", data.get("jobTitle", "")),
        ("Age", data.get("age", "")),
        ("Location", data.get("fullAddress", "")),
        ("Languages", ", ".join(data.get("languages", []))),
        ("Skills", ", ".join(data.get("skills", []))),
        ("Expected Salary", data.get("expectedSalary", "")),
        ("Education", data.get("education", "")),
        ("Years of Experience", data.get("yearsOfExp", "")),
        ("LinkedIn", data.get("socials", {}).get("linkedin", "")),
        ("GitHub", data.get("socials", {}).get("github", "")),
        ("Portfolio", data.get("socials", {}).get("portfolio", ""))
    ]

    for label, value in fields:
        write_line(label, value)

    # Education history (optional)
    education_history = data.get("educationHistory", [])
    if education_history:
        write_line("Education History", "")
        for entry in education_history:
            write_line("•", entry)

    c.save()
    return file_path
