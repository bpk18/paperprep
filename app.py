from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from docx import Document
from fpdf import FPDF
from PIL import Image
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

# Home Page
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
            doc = Document()
            doc.add_paragraph("Converted [Placeholder Content].")
            doc.save(output_path)

            return send_file(output_path, as_attachment=True)
    return render_template('pdf_to_word.html')

# JPG to PDF
@app.route('/jpg-to-pdf', methods=['GET', 'POST'])
def jpg_to_pdf():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            image = Image.open(file_path).convert('RGB')
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.rsplit('.', 1)[0] + '.pdf')
            image.save(output_path)

            return send_file(output_path, as_attachment=True)
    return render_template('jpg_to_pdf.html')

# Merge PDFs
@app.route('/merge-pdfs', methods=['GET', 'POST'])
def merge_pdfs():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files')
        merger = PdfMerger()

        for file in uploaded_files:
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                merger.append(filepath)

        output_path = os.path.join(app.config['CONVERTED_FOLDER'], 'merged.pdf')
        merger.write(output_path)
        merger.close()

        return send_file(output_path, as_attachment=True)
    return render_template('merge_pdfs.html')

# Compress PDF
@app.route('/compress-pdf', methods=['GET', 'POST'])
def compress_pdf():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.pdf'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            reader = PdfReader(file_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            output_path = os.path.join(app.config['CONVERTED_FOLDER'], 'compressed_' + filename)
            with open(output_path, "wb") as f:
                writer.write(f)

            return send_file(output_path, as_attachment=True)
    return render_template('compress_pdf.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Privacy Policy
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Change port to 5001 (or any other free port)

