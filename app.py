from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader
from docx import Document
from fpdf import FPDF
from PIL import Image
import pytesseract
import nltk
import difflib
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# PDF to Word
@app.route('/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.pdf'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.pdf', '.docx'))
            # Placeholder: simulate conversion
            doc = Document()
            doc.add_paragraph("[Simulated] Content extracted from PDF.")
            doc.save(output_path)
            return send_file(output_path, as_attachment=True)
    return render_template('pdf_to_word.html')

# PDF Merger
@app.route('/pdf-merger', methods=['GET', 'POST'])
def pdf_merger():
    if request.method == 'POST':
        files = request.files.getlist('files')
        file_paths = []
        for uploaded_file in files:
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            file_paths.append(file_path)
        
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], 'merged.pdf')
        merger = PdfMerger()
        for file_path in file_paths:
            merger.append(file_path)
        merger.write(output_path)
        merger.close()
        return send_file(output_path, as_attachment=True)
    return render_template('pdf_merger.html')

# PDF Splitter
@app.route('/pdf-splitter', methods=['GET', 'POST'])
def pdf_splitter():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        start_page = int(request.form['start_page'])
        end_page = int(request.form['end_page'])
        if uploaded_file.filename.endswith('.pdf'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            reader = PdfReader(file_path)
            writer = PdfWriter()
            for page_num in range(start_page-1, end_page):
                writer.add_page(reader.pages[page_num])
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.pdf', f'_{start_page}_to_{end_page}.pdf'))
            with open(output_path, 'wb') as output_pdf:
                writer.write(output_pdf)
            return send_file(output_path, as_attachment=True)
    return render_template('pdf_splitter.html')

# Resume Tailoring Tool
@app.route('/resume-tailor', methods=['GET', 'POST'])
def resume_tailor():
    if request.method == 'POST':
        resume_text = request.form['resume_text']
        job_description = request.form['job_description']
        # Simple logic to find missing keywords (could be enhanced)
        missing_keywords = difflib.get_close_matches(resume_text, job_description.split())
        return render_template('resume_tailor_result.html', missing_keywords=missing_keywords)
    return render_template('resume_tailor.html')

# LinkedIn to Resume Converter
@app.route('/linkedin-to-resume', methods=['GET', 'POST'])
def linkedin_to_resume():
    if request.method == 'POST':
        linkedin_data = request.form['linkedin_data']
        # Placeholder logic to parse LinkedIn data
        resume_content = f"Name: {linkedin_data} \nEducation: XYZ University"
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], 'linkedin_resume.pdf')
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(200, 10, txt=resume_content, align='L')
        pdf.output(output_path)
        return send_file(output_path, as_attachment=True)
    return render_template('linkedin_to_resume.html')

# Portfolio PDF Builder
@app.route('/portfolio-builder', methods=['GET', 'POST'])
def portfolio_builder():
    if request.method == 'POST':
        images = request.files.getlist('images')
        descriptions = request.form['descriptions']
        portfolio_content = []
        for img in images:
            filename = secure_filename(img.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(file_path)
            portfolio_content.append(f"Image: {filename}, Description: {descriptions}")
        
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], 'portfolio.pdf')
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(200, 10, txt='\n'.join(portfolio_content), align='L')
        pdf.output(output_path)
        return send_file(output_path, as_attachment=True)
    return render_template('portfolio_builder.html')

# OCR Tool
@app.route('/image-to-text', methods=['GET', 'POST'])
def image_to_text():
    if request.method == 'POST':
        uploaded_image = request.files['file']
        if uploaded_image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filename = secure_filename(uploaded_image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_image.save(image_path)
            text = pytesseract.image_to_string(Image.open(image_path))
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], 'extracted_text.txt')
            with open(output_path, 'w') as f:
                f.write(text)
            return send_file(output_path, as_attachment=True)
    return render_template('image_to_text.html')

# Cover Letter Generator
@app.route('/cover-letter-generator', methods=['GET', 'POST'])
def cover_letter_generator():
    if request.method == 'POST':
        job_title = request.form['job_title']
        experience = request.form['experience']
        # Generate cover letter
        cover_letter = f"Dear Hiring Manager,\n\nI am excited to apply for the {job_title} position. I have {experience} of experience."
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], 'cover_letter.txt')
        with open(output_path, 'w') as f:
            f.write(cover_letter)
        return send_file(output_path, as_attachment=True)
    return render_template('cover_letter_generator.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 






