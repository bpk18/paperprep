from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
from fpdf import FPDF
import os
import io
import zipfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tool/<tool_name>', methods=['GET', 'POST'])
def tool_router(tool_name):
    if tool_name == 'pdf-to-word':
        return render_template('tools/pdf_to_word.html')
    elif tool_name == 'images-to-pdf':
        return image_to_pdf()
    elif tool_name == 'ppt-to-pdf':
        return render_template('tools/ppt_to_pdf.html')
    elif tool_name == 'pdf-to-ppt':
        return render_template('tools/pdf_to_ppt.html')
    elif tool_name == 'merge-pdf':
        return merge_pdf()
    elif tool_name == 'compress-image':
        return render_template('tools/compress_image.html')
    elif tool_name == 'compress-pdf':
        return render_template('tools/compress_pdf.html')
    elif tool_name == 'pdf-splitter':
        return pdf_splitter()
    else:
        return "Tool not found", 404


@app.route('/about')
def about():
    return render_template('pages/about.html')


@app.route('/privacy')
def privacy():
    return render_template('pages/privacy.html')


@app.route('/contact')
def contact():
    return render_template('pages/contact.html')


@app.route('/terms')
def terms():
    return render_template('pages/terms.html')


def merge_pdf():
    if request.method == 'POST':
        files = request.files.getlist('pdfs')
        merger = PdfFileMerger()

        for f in files:
            if f and f.filename.endswith('.pdf'):
                merger.append(PdfReader(f))

        output = io.BytesIO()
        merger.write(output)
        output.seek(0)
        return send_file(output, download_name="merged.pdf", as_attachment=True)
    return render_template('tools/merge_pdf.html')


def image_to_pdf():
    if request.method == 'POST':
        images = request.files.getlist('images')
        pdf = FPDF()
        for img_file in images:
            img = Image.open(img_file)
            img = img.convert('RGB')
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(img_file.filename))
            img.save(img_path)
            width, height = img.size
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=190)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')
        pdf.output(pdf_path)
        return send_file(pdf_path, as_attachment=True)
    return render_template('tools/images_to_pdf.html')


def pdf_splitter():
    if request.method == 'POST':
        file = request.files['pdf']
        if file and file.filename.endswith('.pdf'):
            reader = PdfReader(file)
            zip_stream = io.BytesIO()
            with zipfile.ZipFile(zip_stream, 'w') as zipf:
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    buffer = io.BytesIO()
                    writer.write(buffer)
                    buffer.seek(0)
                    zipf.writestr(f'page_{i+1}.pdf', buffer.read())
            zip_stream.seek(0)
            return send_file(zip_stream, download_name='split_pages.zip', as_attachment=True)
    return render_template('tools/pdf_splitter.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
