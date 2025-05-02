from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Set the upload folder for files
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'ppt', 'docx'}

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tool/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Add the logic to convert PDF to Word here
            # For now, just return the file name (you can replace this with actual conversion)
            return send_file(file_path, as_attachment=True)
    return render_template('tool.html', tool_name="PDF to Word")

@app.route('/tool/images-to-pdf', methods=['GET', 'POST'])
def images_to_pdf():
    if request.method == 'POST':
        files = request.files.getlist('files')
        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_paths.append(file_path)
        
        # Add the logic to convert images to PDF here
        # For now, just return the last file (you can replace this with actual conversion)
        return send_file(file_paths[-1], as_attachment=True)
    return render_template('tool.html', tool_name="Image to PDF")

@app.route('/tool/ppt-to-pdf', methods=['GET', 'POST'])
def ppt_to_pdf():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Add the logic to convert PPT to PDF here
            # For now, just return the file (you can replace this with actual conversion)
            return send_file(file_path, as_attachment=True)
    return render_template('tool.html', tool_name="PPT to PDF")

@app.route('/tool/pdf-to-ppt', methods=['GET', 'POST'])
def pdf_to_ppt():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Add the logic to convert PDF to PPT here
            # For now, just return the file (you can replace this with actual conversion)
            return send_file(file_path, as_attachment=True)
    return render_template('tool.html', tool_name="PDF to PPT")

@app.route('/tool/merge-pdf', methods=['GET', 'POST'])
def merge_pdf():
    if request.method == 'POST':
        files = request.files.getlist('files')
        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                file_paths.append(file_path)
        
        # Add logic to merge PDFs here
        # For now, just return the last uploaded file (you can replace this with actual merging)
        return send_file(file_paths[-1], as_attachment=True)
    return render_template('tool.html', tool_name="Merge PDFs")

@app.route('/tool/pdf-splitter', methods=['GET', 'POST'])
def pdf_splitter():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Add logic to split PDFs here
            # For now, just return the uploaded file (you can replace this with actual splitting)
            return send_file(file_path, as_attachment=True)
    return render_template('tool.html', tool_name="Split PDF")

@app.route('/tool/compress-image', methods=['GET', 'POST'])
def compress_image():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Add the logic to compress the image here
            # For now, just return the uploaded file (you can replace this with actual compression)
            return send_file(file_path, as_attachment=True)
    return render_template('tool.html', tool_name="Compress Image")

@app.route('/tool/compress-pdf', methods=['GET', 'POST'])
def compress_pdf():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Add the logic to compress the PDF here
            # For now, just return the uploaded file (you can replace this with actual compression)
            return send_file(file_path, as_attachment=True)
    return render_template('tool.html', tool_name="Compress PDF")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

if __name__ == '__main__':
    # Run the Flask app on a specific host and port
    app.run(host='0.0.0.0', port=5000, debug=True)
