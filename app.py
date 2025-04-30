from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
from PIL import Image
import img2pdf
import pytesseract
from docx import Document
from pdf2docx import Converter
import fitz  # PyMuPDF
import tempfile
import shutil
import pythoncom
import comtypes.client
from pptx import Presentation

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'ppt', 'pptx', 'doc', 'docx'}

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

            elif tool_name == 'ppt-to-pdf':
                pythoncom.CoInitialize()
                powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
                ppt = powerpoint.Presentations.Open(saved_files[0], WithWindow=False)
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.pdf')
                ppt.SaveAs(output_path, 32)  # 32 = PDF format
                ppt.Close()
                powerpoint.Quit()

            elif tool_name == 'pdf-to-ppt':
                doc = fitz.open(saved_files[0])
                prs = Presentation()
                blank_slide_layout = prs.slide_layouts[6]
                for page in doc:
                    pix = page.get_pixmap()
                    img_path = os.path.join(app.config['OUTPUT_FOLDER'], f"page_{page.number}.png")
                    pix.save(img_path)
                    slide = prs.slides.add_slide(blank_slide_layout)
                    slide.shapes.add_picture(img_path, 0, 0, width=prs.slide_width)
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'converted.pptx')
                prs.save(output_path)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
