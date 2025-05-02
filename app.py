from flask import render_template, request, send_file
# Import necessary libraries for each tool
from PIL import Image
from PyPDF2 import PdfMerger, PdfReader
import io

@app.route('/', methods=['GET'])
def index():
    tools = [
        {'name': 'PDF to Word', 'icon': 'pdf_to_word.png', 'route': '/pdf_to_word'},
        {'name': 'JPG to Word', 'icon': 'jpg_to_word.png', 'route': '/jpg_to_word'},
        {'name': 'PPT to PDF', 'icon': 'ppt_to_pdf.png', 'route': '/ppt_to_pdf'},
        {'name': 'PDF to PPT', 'icon': 'pdf_to_ppt.png', 'route': '/pdf_to_ppt'},
        {'name': 'Merge PDF', 'icon': 'merge_pdf.png', 'route': '/merge_pdf'},
        {'name': 'Multiple Images to PDF', 'icon': 'images_to_pdf.png', 'route': '/images_to_pdf'},
        {'name': 'Image Compressor', 'icon': 'image_compressor.png', 'route': '/image_compressor'},
        {'name': 'PDF Compressor', 'icon': 'pdf_compressor.png', 'route': '/pdf_compressor'},
        # Add other tools here
    ]
    return render_template('index.html', tools=tools)

@app.route('/pdf_to_word', methods=['GET', 'POST'])
def pdf_to_word():
    if request.method == 'POST':
        # Handle PDF to Word conversion logic here
        # This will likely involve external libraries or APIs
        return "PDF to Word functionality will be implemented here."
    return render_template('pdf_to_word.html')

@app.route('/jpg_to_word', methods=['GET', 'POST'])
def jpg_to_word():
    if request.method == 'POST':
        # Handle JPG to Word conversion logic here (OCR might be needed)
        return "JPG to Word functionality will be implemented here."
    return render_template('jpg_to_word.html')

@app.route('/ppt_to_pdf', methods=['GET', 'POST'])
def ppt_to_pdf():
    if request.method == 'POST':
        # Handle PPT to PDF conversion
        return "PPT to PDF functionality will be implemented here."
    return render_template('ppt_to_pdf.html')

@app.route('/pdf_to_ppt', methods=['GET', 'POST'])
def pdf_to_ppt():
    if request.method == 'POST':
        # Handle PDF to PPT conversion (complex, might need external tools)
        return "PDF to PPT functionality will be implemented here."
    return render_template('pdf_to_ppt.html')

@app.route('/merge_pdf', methods=['GET', 'POST'])
def merge_pdf():
    if request.method == 'POST':
        pdfs = request.files.getlist('pdfs')
        merger = PdfMerger()
        for pdf in pdfs:
            pdf_reader = PdfReader(pdf)
            merger.append(pdf_reader)
        output = io.BytesIO()
        merger.write(output)
        output.seek(0)
        return send_file(output, download_name='merged.pdf', as_attachment=True)
    return render_template('merge_pdf.html')

@app.route('/images_to_pdf', methods=['GET', 'POST'])
def images_to_pdf():
    if request.method == 'POST':
        images = request.files.getlist('images')
        if not images:
            return "Please upload at least one image."
        img_list = []
        for image_file in images:
            img = Image.open(image_file)
            if img.mode == "RGBA":
                img = img.convert("RGB")
            img_list.append(img)
        output = io.BytesIO()
        img_list[0].save(output, format="PDF", save_all=True, append_images=img_list[1:])
        output.seek(0)
        return send_file(output, download_name='images.pdf', as_attachment=True)
    return render_template('images_to_pdf.html')

@app.route('/image_compressor', methods=['GET', 'POST'])
def image_compressor():
    if request.method == 'POST':
        image_file = request.files['image']
        quality = int(request.form['quality'])
        img = Image.open(image_file)
        output = io.BytesIO()
        img.save(output, format=img.format, optimize=True, quality=quality)
        output.seek(0)
        return send_file(output, download_name=f'compressed.{img.format.lower()}', as_attachment=True)
    return render_template('image_compressor.html')

@app.route('/pdf_compressor', methods=['GET', 'POST'])
def pdf_compressor():
    if request.method == 'POST':
        pdf_file = request.files['pdf']
        # Implement PDF compression logic here (can be complex)
        # You might explore libraries like Ghostscript or online APIs
        return "PDF compression functionality will be implemented here."
    return render_template('pdf_compressor.html')

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)
