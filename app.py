from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from fpdf import FPDF
from PIL import Image
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge_pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('pdfs[]')
    merger = PdfMerger()
    output_path = os.path.join(PROCESSED_FOLDER, 'merged.pdf')
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        merger.append(filepath)
    merger.write(output_path)
    merger.close()
    return jsonify({'download_url': f'/download/merged.pdf'})

@app.route('/image_to_pdf', methods=['POST'])
def image_to_pdf():
    files = request.files.getlist('images[]')
    pdf = FPDF()
    for file in files:
        img = Image.open(file)
        img_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        img.save(img_path)
        pdf.add_page()
        pdf.image(img_path, x=10, y=10, w=pdf.w - 20)
    output_path = os.path.join(PROCESSED_FOLDER, 'images_combined.pdf')
    pdf.output(output_path)
    return jsonify({'download_url': '/download/images_combined.pdf'})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(PROCESSED_FOLDER, filename), as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


