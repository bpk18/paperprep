from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from docx import Document
from fpdf import FPDF
from PIL import Image
import uuid
from pdf2image import convert_from_path  # To convert PDF to PNG

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
            doc = Document()
            doc.add_paragraph("[Simulated] Content extracted from PDF.")
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

# PDF to PNG
@app.route('/pdf-to-png', methods=['GET', 'POST'])
def pdf_to_png():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.pdf'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            # Convert PDF to PNG
            images = convert_from_path(file_path)
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.pdf', '.png'))
            images[0].save(output_path, 'PNG')

            return send_file(output_path, as_attachment=True)
    return render_template('pdf_to_png.html')

# Word to PDF
@app.route('/word-to-pdf', methods=['GET', 'POST'])
def word_to_pdf():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.docx'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            # Simulate Word to PDF conversion
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.docx', '.pdf'))
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Word to PDF conversion", ln=True)
            pdf.output(output_path)

            return send_file(output_path, as_attachment=True)
    return render_template('word_to_pdf.html')

# Excel to PDF
@app.route('/excel-to-pdf', methods=['GET', 'POST'])
def excel_to_pdf():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.xlsx'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            # Simulate Excel to PDF conversion
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.xlsx', '.pdf'))
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Excel to PDF conversion", ln=True)
            pdf.output(output_path)

            return send_file(output_path, as_attachment=True)
    return render_template('excel_to_pdf.html')

# PDF Merger
@app.route('/pdf-merge', methods=['GET', 'POST'])
def pdf_merge():
    if request.method == 'POST':
        files = request.files.getlist('file')
        pdfs = []
        for uploaded_file in files:
            if uploaded_file.filename.endswith('.pdf'):
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(file_path)
                pdfs.append(file_path)

        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(pdf)
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], 'merged.pdf')
        merger.write(output_path)
        merger.close()

        return send_file(output_path, as_attachment=True)
    return render_template('pdf_merge.html')

if __name__ == '__main__':
    app.run(debug=True)
