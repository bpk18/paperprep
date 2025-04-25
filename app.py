
from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from docx import Document
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.pdf'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.pdf', '.docx'))
            doc = Document()
            doc.add_paragraph("[Simulated] Content from PDF.")
            doc.save(output_path)
            return send_file(output_path, as_attachment=True)
    return '''
        <h2>PDF to Word</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Convert">
        </form>
    '''

@app.route('/word-to-pdf', methods=['GET', 'POST'])
def word_to_pdf():
    return '<h2>[Coming Soon]</h2>'

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
    return '''
        <h2>JPG to PDF</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Convert">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
