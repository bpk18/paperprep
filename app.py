from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from PIL import Image
import PyPDF2
from pdf2docx import Converter
from docx2pdf import convert
from pptx import Presentation
import img2pdf
import io
import zipfile
from flask_compress import Compress
import PIL
from flask_sslify import SSLify
from flask_minify import minify

app = Flask(__name__)
Compress(app)
SSLify(app)
minify(app=app, html=True, js=True, cssless=True)

# SEO Optimization
app.config['SITE_NAME'] = "PAPERPREP - All-in-One Document Conversion Tools"
app.config['SITE_DESCRIPTION'] = "Convert PDF to Word, JPG to Word, PPT to PDF, PDF to PPT, merge PDFs, compress images and PDFs. Fast, secure, and free document conversion tools."

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png', 'ppt', 'pptx'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf-to-word', methods=['POST'])
def pdf_to_word():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        output_file = filepath.rsplit('.', 1)[0] + '.docx'
        cv = Converter(filepath)
        cv.convert(output_file)
        cv.close()
        
        return send_file(output_file, as_attachment=True)
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/jpg-to-word', methods=['POST'])
def jpg_to_word():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and allowed_file(file.filename):
        # Implementation for JPG to Word conversion
        pass

# Similar routes for other conversion tools...

@app.route('/compress-image', methods=['POST'])
def compress_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and allowed_file(file.filename):
        img = Image.open(file)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=60)
        output.seek(0)
        return send_file(output, mimetype='image/jpeg', as_attachment=True, 
                        download_name='compressed_' + file.filename)

@app.route('/merge-pdfs', methods=['POST'])
def merge_pdfs():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    merger = PyPDF2.PdfMerger()
    
    for file in files:
        if file and allowed_file(file.filename):
            merger.append(file)
    
    output = io.BytesIO()
    merger.write(output)
    output.seek(0)
    return send_file(output, mimetype='application/pdf', as_attachment=True,
                    download_name='merged.pdf')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
