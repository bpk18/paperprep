from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf-to-word')
def pdf_to_word():
    return render_template('tools/pdf_to_word.html')

@app.route('/jpg-to-word')
def jpg_to_word():
    return render_template('tools/jpg_to_word.html')

@app.route('/ppt-to-pdf')
def ppt_to_pdf():
    return render_template('tools/ppt_to_pdf.html')

@app.route('/pdf-to-ppt')
def pdf_to_ppt():
    return render_template('tools/pdf_to_ppt.html')

@app.route('/merge-pdfs')
def merge_pdfs():
    return render_template('tools/merge_pdfs.html')

@app.route('/image-compressor')
def image_compressor():
    return render_template('tools/image_compressor.html')

@app.route('/pdf-compressor')
def pdf_compressor():
    return render_template('tools/pdf_compressor.html')

@app.route('/images-to-pdf')
def images_to_pdf():
    return render_template('tools/images_to_pdf.html')

@app.route('/ocr')
def ocr():
    return render_template('tools/ocr.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)