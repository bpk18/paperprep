from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import pytesseract
from PIL import Image
from fpdf import FPDF
import pdf2image
import docx
import tempfile
import difflib

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

# --- PDF Compressor ---
@app.route('/compress', methods=['GET', 'POST'])
def compress_pdf():
    if request.method == 'POST':
        file = request.files['pdf_file']
        input_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(input_path)
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.remove_metadata()
        output_path = os.path.join(OUTPUT_FOLDER, 'compressed_' + file.filename)
        with open(output_path, 'wb') as f:
            writer.write(f)
        return send_file(output_path, as_attachment=True)
    return render_template('compress.html')

# --- Cover Letter Generator ---
@app.route('/cover-letter', methods=['GET', 'POST'])
def cover_letter():
    if request.method == 'POST':
        name = request.form['name']
        job = request.form['job']
        experience = request.form['experience']
        letter = f"Dear Hiring Manager,\n\nMy name is {name} and I am excited to apply for the {job} position. I bring {experience} years of experience...\n\nSincerely,\n{name}"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in letter.split('\n'):
            pdf.cell(200, 10, txt=line, ln=True)
        path = os.path.join(OUTPUT_FOLDER, f"cover_letter_{name}.pdf")
        pdf.output(path)
        return send_file(path, as_attachment=True)
    return render_template('cover_letter.html')

# --- Resume Tailoring Tool ---
@app.route('/resume-tailor', methods=['GET', 'POST'])
def resume_tailor():
    if request.method == 'POST':
        resume = request.form['resume']
        job_desc = request.form['job_desc']
        resume_words = set(resume.lower().split())
        job_words = set(job_desc.lower().split())
        missing_keywords = job_words - resume_words
        return render_template('resume_result.html', missing=', '.join(missing_keywords))
    return render_template('resume_tailor.html')

# --- PDF Merger ---
@app.route('/merge', methods=['GET', 'POST'])
def merge_pdfs():
    if request.method == 'POST':
        files = request.files.getlist('pdf_files')
        merger = PdfMerger()
        for file in files:
            merger.append(file)
        path = os.path.join(OUTPUT_FOLDER, 'merged.pdf')
        with open(path, 'wb') as f:
            merger.write(f)
        return send_file(path, as_attachment=True)
    return render_template('merge.html')

# --- Image to Text (OCR) ---
@app.route('/ocr', methods=['GET', 'POST'])
def ocr():
    if request.method == 'POST':
        file = request.files['image']
        path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(path)
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return render_template('ocr_result.html', text=text)
    return render_template('ocr.html')

# --- Excel to PDF ---
@app.route('/excel-to-pdf', methods=['GET', 'POST'])
def excel_to_pdf():
    if request.method == 'POST':
        return "Coming Soon"
    return render_template('excel_to_pdf.html')

# --- PDF to PNG ---
@app.route('/pdf-to-png', methods=['GET', 'POST'])
def pdf_to_png():
    if request.method == 'POST':
        file = request.files['pdf_file']
        path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(path)
        images = pdf2image.convert_from_path(path)
        img_paths = []
        for i, img in enumerate(images):
            out_path = os.path.join(OUTPUT_FOLDER, f"page_{i+1}.png")
            img.save(out_path)
            img_paths.append(out_path)
        return render_template('pdf_to_png_result.html', images=img_paths)
    return render_template('pdf_to_png.html')

# --- Portfolio PDF Builder ---
@app.route('/portfolio-builder', methods=['GET', 'POST'])
def portfolio_builder():
    if request.method == 'POST':
        images = request.files.getlist('images')
        pdf = FPDF()
        for img_file in images:
            path = os.path.join(UPLOAD_FOLDER, secure_filename(img_file.filename))
            img_file.save(path)
            pdf.add_page()
            pdf.image(path, x=10, y=10, w=180)
        out = os.path.join(OUTPUT_FOLDER, 'portfolio.pdf')
        pdf.output(out)
        return send_file(out, as_attachment=True)
    return render_template('portfolio.html')

# --- Certificate Combiner ---
@app.route('/cert-combine', methods=['GET', 'POST'])
def cert_combine():
    if request.method == 'POST':
        files = request.files.getlist('pdf_files')
        merger = PdfMerger()
        for file in files:
            merger.append(file)
        path = os.path.join(OUTPUT_FOLDER, 'certificates_combined.pdf')
        merger.write(path)
        return send_file(path, as_attachment=True)
    return render_template('cert_combine.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
