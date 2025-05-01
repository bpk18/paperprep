from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF for PDF splitting
from fpdf import FPDF
from PIL import Image
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tool/<tool_name>', methods=['GET', 'POST'])
def tool(tool_name):
    return render_template(f'{tool_name}.html')

@app.route('/pdf-to-word', methods=['POST'])
def pdf_to_word():
    return "PDF to Word functionality coming soon."

@app.route('/images-to-pdf', methods=['POST'])
def images_to_pdf():
    files = request.files.getlist('images')
    images = [Image.open(file).convert('RGB') for file in files if file.filename]

    if images:
        pdf_io = io.BytesIO()
        images[0].save(pdf_io, save_all=True, append_images=images[1:], format='PDF')
        pdf_io.seek(0)
        return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='images_merged.pdf')
    return redirect(url_for('tool', tool_name='images-to-pdf'))

@app.route('/pdf-splitter', methods=['POST'])
def pdf_splitter():
    file = request.files['pdf']
    pdf_reader = PdfReader(file)
    zip_io = io.BytesIO()
    from zipfile import ZipFile

    with ZipFile(zip_io, 'w') as zip_file:
        for i, page in enumerate(pdf_reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            pdf_page_io = io.BytesIO()
            writer.write(pdf_page_io)
            pdf_page_io.seek(0)
            zip_file.writestr(f'page_{i + 1}.pdf', pdf_page_io.read())

    zip_io.seek(0)
    return send_file(zip_io, mimetype='application/zip', as_attachment=True, download_name='split_pages.zip')

@app.route('/ppt-to-pdf', methods=['POST'])
def ppt_to_pdf():
    return "PPT to PDF functionality coming soon."

@app.route('/pdf-to-ppt', methods=['POST'])
def pdf_to_ppt():
    return "PDF to PPT functionality coming soon."

@app.route('/merge-pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('pdfs')
    merger = PdfMerger()

    for file in files:
        if file.filename:
            merger.append(file)

    output = io.BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='merged.pdf')

@app.route('/compress-image', methods=['POST'])
def compress_image():
    return "Image compression functionality coming soon."

@app.route('/compress-pdf', methods=['POST'])
def compress_pdf():
    return "PDF compression functionality coming soon."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
