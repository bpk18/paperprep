from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Supported formats
SUPPORTED_CONVERSIONS = {
    'pdf': ['docx', 'jpg', 'png', 'txt'],
    'docx': ['pdf', 'txt', 'odt'],
    'jpg': ['pdf', 'png', 'webp'],
    'png': ['pdf', 'jpg', 'webp'],
    'txt': ['pdf', 'docx']
}

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get-formats', methods=['POST'])
def get_formats():
    filename = request.json.get('filename', '')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    file_ext = filename.split('.')[-1].lower()
    formats = SUPPORTED_CONVERSIONS.get(file_ext, [])
    
    return jsonify({
        'formats': formats,
        'original_format': file_ext
    })

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    target_format = request.form.get('format')
    if not target_format:
        return jsonify({'error': 'No target format selected'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # In a real app, perform actual conversion here
    # For demo, we'll just return a success response
    new_filename = f"converted_{filename.split('.')[0]}.{target_format}"
    
    return jsonify({
        'success': True,
        'download_url': f'/download/{new_filename}'
    })

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)