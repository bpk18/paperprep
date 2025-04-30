from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import img2pdf
import pytesseract
from docx import Document
from pdf2docx import Converter
import fitz  # PyMuPDF
import tempfile
import shutil
import platform

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'ppt', 'pptx', 'doc', 'docx'}

# Create folders if not exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def clear_output_folder():
    for f in os.listdir(app.config['OUTPUT_FOLDER']):
        os.remove(os.path.join(app.config['OUTPUT_FOLDER'], f))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tool/<tool_name>', methods=['GET', 'POST'])
def tool(tool_name):
    if request.method == 'POST':
        clear_output_folder()
        files = request.files.getlist('file')
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                saved_files.append(path)

        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"output_{tool_name}.pdf")

        try:
            if tool_name == 'pdf-to-word':
                cv = Converter(saved_files[0])
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'converted.docx')
                cv.convert(output_path, start=0, end=None)
                cv.close()

            elif tool_name == 'jpg-to-word':
                doc = Document()
                for img in saved_files:
                    text = pytesseract.image_to_string(Image.open(img))
                    doc.add_paragraph(text)
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.docx')
                doc.save(output_path)

            elif tool_name == 'pdf-splitter':
                input_pdf = PdfReader(saved_files[0])
                writer = PdfWriter()
                output_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'split_pdfs')
                os.makedirs(output_dir, exist_ok=True)

                for page_num in range(len(input_pdf.pages)):
                    writer.add_page(input_pdf.pages[page_num])
                    output_filename = os.path.join(output_dir, f"split_page_{page_num + 1}.pdf")
                    with open(output_filename, 'wb') as output_file:
                        writer.write(output_file)

                output_path = output_dir

            elif tool_name == 'images-to-pdf':
                image_list = [Image.open(img).convert("RGB") for img in saved_files]
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'merged.pdf')
                image_list[0].save(output_path, save_all=True, append_images=image_list[1:])

            elif tool_name == 'merge-pdf':
                merger = PdfMerger()
                for pdf in saved_files:
                    merger.append(pdf)
                merger.write(output_path)
                merger.close()

            elif tool_name == 'compress-image':
                img = Image.open(saved_files[0])
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'compressed.jpg')
                img.save(output_path, optimize=True, quality=40)

            elif tool_name == 'compress-pdf':
                pdf_file = fitz.open(saved_files[0])
                for page in pdf_file:
                    page.compress_content_streams()
                pdf_file.save(output_path, garbage=4, deflate=True)

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            return f"Error processing file: {str(e)}"

    return render_template('tool.html', tool=tool_name)

# === robots.txt route ===
@app.route('/robots.txt')
def robots():
    return send_file(os.path.join(app.static_folder, 'robots.txt'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
