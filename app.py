from flask import Flask, render_template, request, send_file, jsonify
import os, uuid
from werkzeug.utils import secure_filename
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract

app = Flask(__name__)
UPLOAD = 'uploads'
RESULT = 'results'
os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(RESULT, exist_ok=True)

def save_and_get_path(file, folder=UPLOAD):
    fn = secure_filename(file.filename)
    path = os.path.join(folder, fn)
    file.save(path)
    return path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resume-tailor', methods=['POST'])
def resume_tailor():
    in_path = save_and_get_path(request.files['resume_file'])
    jd = request.form['job_description'].lower().split()
    with open(in_path, 'r', errors='ignore') as f:
        text = f.read().lower()
    missing = [w for w in jd if w not in text]
    out_path = os.path.join(RESULT, f"resume_{uuid.uuid4().hex}.txt")
    with open(out_path, 'w') as f:
        f.write("Missing Keywords:\\n" + "\\n".join(missing))
    return jsonify({'file': '/' + out_path})

@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    title = request.form['job_title']
    exp = request.form['experience']
    doc = Document()
    doc.add_paragraph(f"Cover Letter for {title}")
    doc.add_paragraph(exp)
    out_fn = f"cover_{uuid.uuid4().hex}.docx"
    out_path = os.path.join(RESULT, out_fn)
    doc.save(out_path)
    return jsonify({'file': '/' + out_path})

@app.route('/convert-pdf-to-word', methods=['POST'])
def convert_pdf_to_word():
    path = save_and_get_path(request.files['pdf_file'])
    reader = PdfReader(path)
    text = "".join(page.extract_text() or "" for page in reader.pages)
    doc = Document()
    doc.add_paragraph(text)
    out_fn = f"word_{uuid.uuid4().hex}.docx"
    out_path = os.path.join(RESULT, out_fn)
    doc.save(out_path)
    return jsonify({'file': '/' + out_path})

@app.route('/convert-jpg-to-pdf', methods=['POST'])
def convert_jpg_to_pdf():
    path = save_and_get_path(request.files['jpg_file'])
    img = Image.open(path).convert('RGB')
    out_fn = f"jpg2pdf_{uuid.uuid4().hex}.pdf"
    out_path = os.path.join(RESULT, out_fn)
    img.save(out_path)
    return jsonify({'file': '/' + out_path})

# Static serving
@app.route('/uploads/<path:p>')
def serve_upload(p): return send_file(os.path.join(UPLOAD, p))
@app.route('/results/<path:p>')
def serve_result(p): return send_file(os.path.join(RESULT, p))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
