
from flask import Flask, render_template, request, send_file, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from fpdf import FPDF
from docx import Document
from PyPDF2 import PdfReader, PdfWriter
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Route: Home page
@app.route('/')
def index():
    return render_template('index.html')

# Tool 1: Resume Tailoring Tool
@app.route('/resume-tailor', methods=['POST'])
def resume_tailor():
    resume_file = request.files['resume_file']
    job_desc = request.form['job_description']
    resume_path = os.path.join(UPLOAD_FOLDER, secure_filename(resume_file.filename))
    resume_file.save(resume_path)

    # Basic keyword matching (simulation)
    with open(resume_path, 'r', encoding='utf-8', errors='ignore') as f:
        resume_text = f.read()

    keywords = job_desc.lower().split()
    missing_keywords = [kw for kw in keywords if kw not in resume_text.lower()]

    result_path = os.path.join(RESULT_FOLDER, f"tailored_resume_{uuid.uuid4().hex}.txt")
    with open(result_path, 'w') as f:
        f.write("Missing Keywords in Resume:\n")
        f.write("\n".join(missing_keywords))

    return jsonify({'file': '/' + result_path})

# Tool 2: Cover Letter Generator
@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    job_title = request.form['job_title']
    experience = request.form['experience']

    doc = Document()
    doc.add_heading('Cover Letter', 0)
    doc.add_paragraph(f"Dear Hiring Manager,")
    doc.add_paragraph(f"I am writing to apply for the position of {job_title}.")
    doc.add_paragraph(f"My experience includes: {experience}")
    doc.add_paragraph("Thank you for considering my application.")
    filename = f"cover_letter_{uuid.uuid4().hex}.docx"
    path = os.path.join(RESULT_FOLDER, filename)
    doc.save(path)
    return jsonify({'file': '/' + path})

# Tool 3: PDF to Word
@app.route('/convert-pdf-to-word', methods=['POST'])
def convert_pdf_to_word():
    pdf_file = request.files['pdf_file']
    path = os.path.join(UPLOAD_FOLDER, secure_filename(pdf_file.filename))
    pdf_file.save(path)

    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    doc = Document()
    doc.add_paragraph(text)
    word_path = os.path.join(RESULT_FOLDER, f"converted_{uuid.uuid4().hex}.docx")
    doc.save(word_path)
    return jsonify({'file': '/' + word_path})

# Tool 4: JPG to PDF
@app.route('/convert-jpg-to-pdf', methods=['POST'])
def convert_jpg_to_pdf():
    jpg_file = request.files['jpg_file']
    img_path = os.path.join(UPLOAD_FOLDER, secure_filename(jpg_file.filename))
    jpg_file.save(img_path)

    image = Image.open(img_path)
    rgb_im = image.convert('RGB')
    pdf_path = os.path.join(RESULT_FOLDER, f"image_{uuid.uuid4().hex}.pdf")
    rgb_im.save(pdf_path)
    return jsonify({'file': '/' + pdf_path})

# Static file serving
@app.route('/uploads/<path:filename>')
def uploaded_files(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

@app.route('/results/<path:filename>')
def result_files(filename):
    return send_file(os.path.join(RESULT_FOLDER, filename))

# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True, port=5000)

