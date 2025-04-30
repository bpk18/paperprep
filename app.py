from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import PyPDF2
from fpdf import FPDF
import io
import difflib

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf_compressor', methods=['GET', 'POST'])
def pdf_compressor():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"compressed_{filename}")
        file.save(input_path)
        doc = fitz.open(input_path)
        for page in doc:
            for img in page.get_images(full=True):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix = fitz.Pixmap(pix, 100, 100)  # Resize to compress
                doc._deleteObject(xref)
                new_xref = doc._addImage(pix.tobytes(), compress=True)
                page.insert_image(page.rect, xref=new_xref)
        doc.save(output_path)
        return send_file(output_path, as_attachment=True)
    return render_template('pdf_compressor.html')

@app.route('/ocr_image_to_text', methods=['GET', 'POST'])
def ocr_image_to_text():
    if request.method == 'POST':
        file = request.files['image']
        img_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(img_path)
        text = pytesseract.image_to_string(Image.open(img_path))
        return render_template('ocr_image_to_text.html', extracted_text=text)
    return render_template('ocr_image_to_text.html')

@app.route('/pdf_merger', methods=['GET', 'POST'])
def pdf_merger():
    if request.method == 'POST':
        files = request.files.getlist('files')
        merger = PyPDF2.PdfMerger()
        paths = []
        for file in files:
            filename = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            paths.append(path)
            merger.append(path)
        output_path = os.path.join(OUTPUT_FOLDER, 'merged.pdf')
        merger.write(output_path)
        merger.close()
        return send_file(output_path, as_attachment=True)
    return render_template('pdf_merger.html')

@app.route('/pdf_splitter', methods=['GET', 'POST'])
def pdf_splitter():
    if request.method == 'POST':
        file = request.files['file']
        page_range = request.form['range']
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        reader = PyPDF2.PdfReader(path)
        writer = PyPDF2.PdfWriter()
        start, end = map(int, page_range.split('-'))
        for i in range(start-1, end):
            writer.add_page(reader.pages[i])
        output_path = os.path.join(OUTPUT_FOLDER, 'split.pdf')
        with open(output_path, 'wb') as f:
            writer.write(f)
        return send_file(output_path, as_attachment=True)
    return render_template('pdf_splitter.html')

@app.route('/password_remover', methods=['GET', 'POST'])
def password_remover():
    if request.method == 'POST':
        file = request.files['file']
        password = request.form['password']
        path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(path)
        reader = PyPDF2.PdfReader(path)
        if reader.is_encrypted:
            reader.decrypt(password)
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        output_path = os.path.join(OUTPUT_FOLDER, 'unlocked.pdf')
        with open(output_path, 'wb') as f:
            writer.write(f)
        return send_file(output_path, as_attachment=True)
    return render_template('password_remover.html')

@app.route('/resume_tailoring', methods=['GET', 'POST'])
def resume_tailoring():
    if request.method == 'POST':
        resume_text = request.form['resume']
        job_desc = request.form['job']
        resume_words = set(resume_text.lower().split())
        job_words = set(job_desc.lower().split())
        missing = job_words - resume_words
        return render_template('resume_tailoring.html', missing_keywords=missing)
    return render_template('resume_tailoring.html')

@app.route('/linkedin_to_resume', methods=['GET', 'POST'])
def linkedin_to_resume():
    if request.method == 'POST':
        profile_text = request.form['linkedin']
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in profile_text.split('\n'):
            pdf.cell(200, 10, txt=line, ln=True)
        output_path = os.path.join(OUTPUT_FOLDER, 'resume.pdf')
        pdf.output(output_path)
        return send_file(output_path, as_attachment=True)
    return render_template('linkedin_to_resume.html')

@app.route('/portfolio_builder', methods=['GET', 'POST'])
def portfolio_builder():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt=title, ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, desc)
        output_path = os.path.join(OUTPUT_FOLDER, 'portfolio.pdf')
        pdf.output(output_path)
        return send_file(output_path, as_attachment=True)
    return render_template('portfolio_builder.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
