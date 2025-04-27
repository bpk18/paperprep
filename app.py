from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import openpyxl
from fpdf import FPDF

app = Flask(__name__)

# Configuration
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

            # Extract text from PDF
            with open(file_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()

            # Save text into a Word document
            doc = Document()
            doc.add_paragraph(text)
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.pdf', '.docx'))
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

            # Convert JPG to PDF
            image = Image.open(file_path).convert('RGB')
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.rsplit('.', 1)[0] + '.pdf')
            image.save(output_path)
            return send_file(output_path, as_attachment=True)
    return render_template('jpg_to_pdf.html')

# Excel to PDF
@app.route('/excel-to-pdf', methods=['GET', 'POST'])
def excel_to_pdf():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.lower().endswith(('.xls', '.xlsx')):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            # Read Excel file
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active

            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            # Write Excel data to PDF
            for row in sheet.iter_rows(values_only=True):
                pdf.cell(200, 10, txt="  ".join(str(cell) for cell in row), ln=True)

            # Save PDF
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.xlsx', '.pdf').replace('.xls', '.pdf'))
            pdf.output(output_path)

            return send_file(output_path, as_attachment=True)

    return render_template('excel_to_pdf.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Run on port 5001 instead of the default 5000

