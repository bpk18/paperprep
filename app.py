from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'pptx', 'docx'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Tool routes
@app.route('/tool/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Implement conversion logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('tool.html', tool_name='PDF to Word')

@app.route('/tool/images-to-pdf', methods=['GET', 'POST'])
def images_to_pdf():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Implement conversion logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('tool.html', tool_name='Image to PDF')

@app.route('/tool/ppt-to-pdf', methods=['GET', 'POST'])
def ppt_to_pdf():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Implement conversion logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('tool.html', tool_name='PPT to PDF')

@app.route('/tool/pdf-to-ppt', methods=['GET', 'POST'])
def pdf_to_ppt():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Implement conversion logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('tool.html', tool_name='PDF to PPT')

@app.route('/tool/merge-pdf', methods=['GET', 'POST'])
def merge_pdf():
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Implement merge logic here
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], 'merged.pdf'), as_attachment=True)
    return render_template('tool.html', tool_name='Merge PDFs')

@app.route('/tool/pdf-splitter', methods=['GET', 'POST'])
def split_pdf():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Implement split logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('tool.html', tool_name='Split PDF')

@app.route('/tool/compress-image', methods=['GET', 'POST'])
def compress_image():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Implement compression logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('tool.html', tool_name='Compress Image')

@app.route('/tool/compress-pdf', methods=['GET', 'POST'])
def compress_pdf():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Implement compression logic here
            return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    return render_template('tool.html', tool_name='Compress PDF')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
