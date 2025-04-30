from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from fpdf import FPDF
import fitz
import pdfminer
import io

app = Flask(__name__)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'}

# Create upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# PDF to Word tool route
@app.route('/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Convert PDF to Word logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('pdf_to_word.html')

# JPG to PDF tool route
@app.route('/jpg-to-pdf', methods=['GET', 'POST'])
def jpg_to_pdf():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Convert JPG to PDF logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('jpg_to_pdf.html')

# Excel to PDF tool route
@app.route('/excel-to-pdf', methods=['GET', 'POST'])
def excel_to_pdf():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Convert Excel to PDF logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('excel_to_pdf.html')

# PDF Merger tool route
@app.route('/pdf-merger', methods=['GET', 'POST'])
def pdf_merger():
    if request.method == 'POST':
        files = request.files.getlist('files')
        pdf_writer = PyPDF2.PdfWriter()
        for file in files:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                pdf_reader = PyPDF2.PdfReader(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
        merged_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'merged.pdf')
        with open(merged_filename, 'wb') as merged_pdf:
            pdf_writer.write(merged_pdf)
        return send_file(merged_filename, as_attachment=True)
    return render_template('pdf_merger.html')

# Resume Tailoring Tool route
@app.route('/resume-tailor', methods=['GET', 'POST'])
def resume_tailor():
    if request.method == 'POST':
        resume_file = request.files['resume']
        job_description_file = request.files['job_description']
        if resume_file and job_description_file and allowed_file(resume_file.filename) and allowed_file(job_description_file.filename):
            resume_filename = secure_filename(resume_file.filename)
            job_description_filename = secure_filename(job_description_file.filename)
            resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename))
            job_description_file.save(os.path.join(app.config['UPLOAD_FOLDER'], job_description_filename))
            # Logic to tailor resume based on job description goes here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], resume_filename), as_attachment=True)
    return render_template('resume_tailor.html')

# LinkedIn to Resume Converter route
@app.route('/linkedin-to-resume', methods=['GET', 'POST'])
def linkedin_to_resume():
    if request.method == 'POST':
        linkedin_url = request.form['linkedin_url']
        # Logic to parse LinkedIn profile and convert to resume goes here
        return send_file('generated_resume.pdf', as_attachment=True)
    return render_template('linkedin_to_resume.html')

# Portfolio PDF Builder route
@app.route('/portfolio-builder', methods=['GET', 'POST'])
def portfolio_builder():
    if request.method == 'POST':
        files = request.files.getlist('images')
        descriptions = request.form.getlist('descriptions')
        # Logic to create portfolio PDF goes here
        return send_file('portfolio.pdf', as_attachment=True)
    return render_template('portfolio_builder.html')

# PDF Password Remover tool route
@app.route('/pdf-password-remover', methods=['GET', 'POST'])
def pdf_password_remover():
    if request.method == 'POST':
        file = request.files['file']
        password = request.form['password']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Logic to remove PDF password goes here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('pdf_password_remover.html')

# Image to Text (OCR) tool route
@app.route('/image-to-text', methods=['GET', 'POST'])
def image_to_text():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Convert image to text (OCR) logic
            text = pytesseract.image_to_string(Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
            return render_template('ocr_result.html', text=text)
    return render_template('image_to_text.html')

# PDF Splitter tool route
@app.route('/pdf-splitter', methods=['GET', 'POST'])
def pdf_splitter():
    if request.method == 'POST':
        file = request.files['file']
        page_range = request.form['page_range']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Logic to split PDF based on page range goes here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('pdf_splitter.html')

# PDF to PNG tool route
@app.route('/pdf-to-png', methods=['GET', 'POST'])
def pdf_to_png():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Logic to convert PDF to PNG goes here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('pdf_to_png.html')

# Certificate Combiner tool route
@app.route('/certificate-combiner', methods=['GET', 'POST'])
def certificate_combiner():
    if request.method == 'POST':
        files = request.files.getlist('files')
        pdf_writer = PyPDF2.PdfWriter()
        for file in files:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                pdf_reader = PyPDF2.PdfReader(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
        combined_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'combined_certificates.pdf')
        with open(combined_filename, 'wb') as combined_pdf:
            pdf_writer.write(combined_pdf)
        return send_file(combined_filename, as_attachment=True)
    return render_template('certificate_combiner.html')

if __name__ == '__main__':
    app.run(debug=True)
