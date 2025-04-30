from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
import PyPDF2
from PIL import Image
import pytesseract
from fpdf import FPDF
from pdf2image import convert_from_path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

# Add your tool routes here — examples below:
@app.route('/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    return render_template('pdf_to_word.html')

@app.route('/jpg-to-pdf', methods=['GET', 'POST'])
def jpg_to_pdf():
    return render_template('jpg_to_pdf.html')

@app.route('/resume-tailor', methods=['GET', 'POST'])
def resume_tailor():
    return render_template('resume_tailor.html')

@app.route('/linkedin-to-resume', methods=['GET', 'POST'])
def linkedin_to_resume():
    return render_template('linkedin_to_resume.html')

@app.route('/portfolio-builder', methods=['GET', 'POST'])
def portfolio_builder():
    return render_template('portfolio_builder.html')

@app.route('/excel-to-pdf', methods=['GET', 'POST'])
def excel_to_pdf():
    return render_template('excel_to_pdf.html')

@app.route('/pdf-merger', methods=['GET', 'POST'])
def pdf_merger():
    return render_template('pdf_merger.html')

@app.route('/pdf-password-remover', methods=['GET', 'POST'])
def pdf_password_remover():
    return render_template('pdf_password_remover.html')

@app.route('/image-to-text', methods=['GET', 'POST'])
def image_to_text():
    return render_template('image_to_text.html')

@app.route('/pdf-splitter', methods=['GET', 'POST'])
def pdf_splitter():
    return render_template('pdf_splitter.html')

@app.route('/pdf-to-png', methods=['GET', 'POST'])
def pdf_to_png():
    return render_template('pdf_to_png.html')

@app.route('/certificate-combiner', methods=['GET', 'POST'])
def certificate_combiner():
    return render_template('certificate_combiner.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
