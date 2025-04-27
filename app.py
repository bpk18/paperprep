from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from docx import Document
from fpdf import FPDF
from PIL import Image
import uuid

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

# Other tools (add as necessary)
# Example tool: Word to PDF (placeholder)
@app.route('/word-to-pdf', methods=['GET', 'POST'])
def word_to_pdf():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.docx'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.docx', '.pdf'))
            # Placeholder: simulate conversion
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Simulated content extracted from Word.", ln=True)
            pdf.output(output_path)
            return send_file(output_path, as_attachment=True)
    return render_template('word_to_pdf.html')

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
    app.run(debug=True, host='0.0.0.0', port=5000)
