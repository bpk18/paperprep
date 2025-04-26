from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import magic
import subprocess
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
    # This is a placeholder - in a real app you'd use actual conversion tools
    # like LibreOffice, FFmpeg, ImageMagick, etc.
    output_path = os.path.join(
        app.config['UPLOAD_FOLDER'],
        f"converted_{datetime.now().strftime('%Y%m%d%H%M%S')}.{output_ext}"
    )
    
    # Simulate conversion by copying the file (replace with actual conversion)
    with open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            output_ext = request.form.get('output_format')
            if not output_ext:
                flash('Please select an output format', 'error')
                return redirect(request.url)
            
            try:
                # Simulate processing delay
                time.sleep(2)
                
                output_path = convert_file(input_path, output_ext)
                return jsonify({
                    'status': 'success',
                    'download_url': url_for('download', filename=os.path.basename(output_path))
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Conversion failed: {str(e)}'
                }), 500
        
        else:
            return jsonify({
                'status': 'error',
                'message': 'File type not supported'
            }), 400
    
    return render_template('index.html', conversions=SUPPORTED_CONVERSIONS)

@app.route('/get-output-formats', methods=['POST'])
def get_output_formats():
    data = request.get_json()
    input_ext = data.get('ext', '')
    
    formats = []
    for category in SUPPORTED_CONVERSIONS.values():
        if input_ext.lower() in category['input']:
            formats = category['output']
            break
    
    return jsonify({'formats': formats})

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            output_ext = request.form.get('output_format')
            if not output_ext:
                flash('Please select an output format', 'error')
                return redirect(request.url)
            
            try:
                output_path = convert_file(input_path, output_ext)
                return redirect(url_for('download', filename=os.path.basename(output_path)))
            except Exception as e:
                flash(f'Conversion failed: {str(e)}', 'error')
                return redirect(request.url)
        
        else:
            flash('File type not supported', 'error')
            return redirect(request.url)
    
    return render_template('index.html', conversions=SUPPORTED_CONVERSIONS)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/features')
def features():
    return render_template('features.html')
# Add this to your existing app.py
@app.context_processor
def inject_brand():
    return {
        'brand_name': 'PaperPrep',
        'brand_tagline': 'Smart Document Preparation',
        'brand_icon': 'file-earmark-text'  # Bootstrap icon
    }

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)