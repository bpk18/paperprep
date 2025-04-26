from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import shutil
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'converted'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'jpg', 'png', 'txt'}

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-formats', methods=['POST'])
def get_formats():
    if not request.json or 'filename' not in request.json:
        return jsonify({'error': 'No filename provided'}), 400
    
    filename = request.json['filename']
    if not allowed_file(filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    file_ext = filename.split('.')[-1].lower()
    
    conversion_map = {
        'pdf': ['docx', 'txt', 'jpg', 'png'],
        'docx': ['pdf', 'txt'],
        'jpg': ['pdf', 'png'],
        'png': ['pdf', 'jpg'],
        'txt': ['pdf', 'docx']
    }
    
    formats = conversion_map.get(file_ext, [])
    return jsonify({'formats': formats, 'original_format': file_ext})

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    target_format = request.form.get('format')
    if not target_format:
        return jsonify({'error': 'No target format selected'}), 400
    
    try:
        # Save original file
        original_filename = secure_filename(file.filename)
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(original_path)
        
        # Create converted filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{original_filename.rsplit('.', 1)[0]}_{timestamp}.{target_format}"
        new_path = os.path.join(app.config['DOWNLOAD_FOLDER'], new_filename)
        
        # ACTUAL CONVERSION WOULD HAPPEN HERE
        # For demo, we just copy the file and change extension
        shutil.copy2(original_path, new_path)
        
        # Clean up original
        os.remove(original_path)
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{new_filename}',
            'filename': new_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        # Security check
        if '..' in filename or filename.startswith('/'):
            abort(400)
        
        return send_from_directory(
            app.config['DOWNLOAD_FOLDER'],
            filename,
            as_attachment=True,
            mimetype='application/octet-stream'
        )
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)