from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from fpdf import FPDF
from PIL import Image

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

# Excel to PDF
@app.route('/excel-to-pdf', methods=['GET', 'POST'])
def excel_to_pdf():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.lower().endswith(('.xls', '.xlsx')):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            # Placeholder: simulate conversion
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.xlsx', '.pdf').replace('.xls', '.pdf'))
            # Actual conversion logic for Excel to PDF should go here
            return send_file(output_path, as_attachment=True)
    return render_template('excel_to_pdf.html')

if __name__ == '__main__':
    app.run(debug=True)
