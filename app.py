from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import time
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Supported conversions
SUPPORTED_CONVERSIONS = {
    'document': {
        'input': ['doc', 'docx', 'odt', 'rtf', 'txt', 'pdf'],
        'output': ['pdf', 'docx', 'txt', 'odt', 'rtf'],
        'icon': 'file-text'
    },
    'image': {
        'input': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff', 'svg'],
        'output': ['jpg', 'png', 'webp', 'gif', 'bmp', 'svg'],
        'icon': 'file-image'
    },
    'audio': {
        'input': ['mp3', 'wav', 'ogg', 'flac', 'aac', 'wma'],
        'output': ['mp3', 'wav', 'ogg', 'flac', 'aac'],
        'icon': 'file-audio'
    },
    'video': {
        'input': ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'],
        'output': ['mp4', 'avi', 'mov', 'webm', 'gif'],
        'icon': 'file-video'
    },
    'archive': {
        'input': ['zip', 'rar', '7z', 'tar', 'gz'],
        'output': ['zip', 'tar', '7z'],
        'icon': 'file-archive'
    }
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in get_all_input_extensions()

def get_all_input_extensions():
    extensions = []
    for category in SUPPORTED_CONVERSIONS.values():
        extensions.extend(category['input'])
    return extensions

def get_output_formats(input_ext):
    for category in SUPPORTED_CONVERSIONS.values():
        if input_ext.lower() in category['input']:
            return category['output']
    return []

def convert_file(input_path, output_ext):
    # In a real app, replace this with actual conversion logic
    # Using FFmpeg, LibreOffice, or other conversion tools
    
    # Simulate conversion time
    time.sleep(2)
    
    output_filename = f"converted_{datetime.now().strftime('%Y%m%d%H%M%S')}.{output_ext}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # Simulate conversion by copying the file
    with open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    return output_path

@app.context_processor
def inject_brand():
    return {
        'brand_name': 'PaperPrep',
        'brand_tagline': 'Smart Document Preparation',
        'brand_icon': 'file-earmark-text'
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle AJAX requests differently
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_ajax_conversion()
            
        return handle_regular_form_submission()
    
    return render_template('index.html', conversions=SUPPORTED_CONVERSIONS)

def handle_ajax_conversion():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'File type not supported'}), 400
        
    try:
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        output_ext = request.form.get('output_format')
        if not output_ext:
            return jsonify({'status': 'error', 'message': 'Output format not specified'}), 400
            
        output_path = convert_file(input_path, output_ext)
        
        return jsonify({
            'status': 'success',
            'download_url': url_for('download', filename=os.path.basename(output_path))
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def handle_regular_form_submission():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
        
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
        
    if not allowed_file(file.filename):
        flash('File type not supported', 'error')
        return redirect(request.url)
        
    try:
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        output_ext = request.form.get('output_format')
        if not output_ext:
            flash('Output format not specified', 'error')
            return redirect(request.url)
            
        output_path = convert_file(input_path, output_ext)
        return redirect(url_for('download', filename=os.path.basename(output_path)))
        
    except Exception as e:
        flash(f'Conversion failed: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/get-output-formats', methods=['POST'])
def api_get_output_formats():
    data = request.get_json()
    if not data or 'ext' not in data:
        return jsonify({'error': 'Extension not provided'}), 400
        
    input_ext = data['ext'].lower().replace('.', '')
    formats = get_output_formats(input_ext)
    return jsonify({'formats': formats})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)