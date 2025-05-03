from flask import Flask, render_template, request, jsonify, send_file
from io import BytesIO
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

# For demo purposes: stub endpoints with no real conversion, just echo file received or dummy response

def save_upload_file(file_storage):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    file_storage.save(temp_file.name)
    return temp_file.name

@app.route('/api/pdf-to-word', methods=['POST'])
def pdf_to_word():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    # Stub: return dummy word doc content
    dummy_content = b'This is a dummy Word document content for pdf-to-word conversion.'
    return send_file(BytesIO(dummy_content), download_name='converted.docx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

@app.route('/api/jpg-to-word', methods=['POST'])
def jpg_to_word():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    dummy_content = b'This is a dummy Word document content for jpg-to-word conversion.'
    return send_file(BytesIO(dummy_content), download_name='converted.docx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

@app.route('/api/ppt-to-pdf', methods=['POST'])
def ppt_to_pdf():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    dummy_pdf = b'%PDF-1.4 Dummy PDF content for ppt-to-pdf conversion'
    return send_file(BytesIO(dummy_pdf), download_name='converted.pdf', as_attachment=True, mimetype='application/pdf')

@app.route('/api/pdf-to-ppt', methods=['POST'])
def pdf_to_ppt():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    dummy_ppt = b'Dummy PPT content for pdf-to-ppt conversion'
    return send_file(BytesIO(dummy_ppt), download_name='converted.pptx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')

@app.route('/api/images-to-pdf', methods=['POST'])
def images_to_pdf():
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        return jsonify({'error': 'No files uploaded'}), 400
    dummy_pdf = b'%PDF-1.4 Dummy PDF for multiple images to pdf conversion'
    return send_file(BytesIO(dummy_pdf), download_name='combined.pdf', as_attachment=True, mimetype='application/pdf')

@app.route('/api/merge-pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        return jsonify({'error': 'No files uploaded'}), 400
    dummy_pdf = b'%PDF-1.4 Dummy PDF for merged pdf'
    return send_file(BytesIO(dummy_pdf), download_name='merged.pdf', as_attachment=True, mimetype='application/pdf')

@app.route('/api/image-compress', methods=['POST'])
def image_compress():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    # Return same file as "compressed"
    return send_file(file, download_name='compressed_'+file.filename, as_attachment=True, mimetype=file.mimetype)

@app.route('/api/pdf-compress', methods=['POST'])
def pdf_compress():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    # Return same file as "compressed"
    return send_file(file, download_name='compressed_'+file.filename, as_attachment=True, mimetype=file.mimetype)

@app.route('/api/other-conversion', methods=['POST'])
def other_conversion():
    return jsonify({'message': 'This tool is not implemented yet.'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
