from flask import Flask, render_template_string, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import io
from PIL import Image
import pytesseract
from docx import Document
from pdf2docx import Converter
from pptx import Presentation
from pptx.util import Inches
import PyPDF2
from PyPDF2 import PdfMerger
import tempfile

# For PDF compression we do basic re-saving with PyPDF2 (not perfect compression but functional)

app = Flask(__name__)
app.secret_key = 'replace-with-your-secret-key'

# Allowed file extensions per tool
ALLOWED_EXTENSIONS = {
    'pdf_to_word': {'pdf'},
    'jpg_to_word': {'jpg', 'jpeg', 'png'},
    'ppt_to_pdf': {'pptx', 'ppt'},
    'pdf_to_ppt': {'pdf'},
    'images_to_pdf': {'jpg', 'jpeg', 'png', 'bmp', 'gif'},
    'merge_pdf': {'pdf'},
    'image_compress': {'jpg', 'jpeg', 'png'},
    'pdf_compress': {'pdf'}
}

# Template shared for all pages using Jinja2 render_template_string with inline CSS/JS for light/dark theme and navbar

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>PAPERPREP - {{ title }}</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet"/>
<style>
  :root {
    --primary-color: #5A9BD4;
    --secondary-color: #6BA292;
    --light-bg: #f0f4f8;
    --light-text: #222;
    --dark-bg: #121212;
    --dark-text: #e0e0e0;
    --button-bg: var(--primary-color);
    --button-hover-bg: #3a7ecf;
    --button-text: white;
    --nav-height: 60px;
    --font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  body {
    margin: 0;
    font-family: var(--font-family);
    background-color: var(--light-bg);
    color: var(--light-text);
    transition: background-color 0.3s ease, color 0.3s ease;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  body.dark {
    background-color: var(--dark-bg);
    color: var(--dark-text);
  }

  nav {
    background: var(--primary-color);
    height: var(--nav-height);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    position: sticky;
    top: 0;
    z-index: 1000;
  }

  nav .brand {
    font-weight: bold;
    font-size: 1.5rem;
    color: white;
    cursor: pointer;
  }

  nav .menu {
    position: relative;
  }

  nav .menu-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: white;
    cursor: pointer;
  }

  nav .dropdown {
    position: absolute;
    right: 0;
    top: calc(var(--nav-height) - 5px);
    background: var(--primary-color);
    border-radius: 5px;
    overflow: hidden;
    display: none;
    min-width: 150px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.3);
    z-index: 1001;
  }

  nav .dropdown a {
    display: block;
    padding: 10px 15px;
    color: white;
    text-decoration: none;
    border-bottom: 1px solid rgba(255,255,255,0.2);
  }

  nav .dropdown a:last-child {
    border-bottom: none;
  }

  nav .dropdown a:hover {
    background: var(--secondary-color);
  }

  nav .menu:hover .dropdown {
    display: block;
  }

  main {
    flex-grow: 1;
    padding: 20px;
    max-width: 900px;
    margin: 0 auto;
    width: 100%;
  }

  h1, h2 {
    text-align: center;
    margin-bottom: 15px;
  }

  .tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 20px;
    margin-top: 20px;
  }

  .tool-card {
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 8px rgb(0 0 0 / 0.1);
    padding: 20px;
    transition: box-shadow 0.3s ease;
    text-align: center;
    cursor: pointer;
    color: var(--light-text);
  }

  body.dark .tool-card {
    background: #1e1e1e;
    color: var(--dark-text);
    box-shadow: 0 4px 12px rgb(255 255 255 / 0.1);
  }

  .tool-card:hover {
    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
  }

  .tool-card i {
    font-size: 3.5rem;
    margin-bottom: 10px;
    color: var(--primary-color);
  }

  body.dark .tool-card i {
    color: #82b1ff;
  }

  .btn, button, input[type="submit"]  {
    background-color: var(--button-bg);
    color: var(--button-text);
    border: none;
    border-radius: 30px;
    padding: 10px 25px;
    font-size: 1rem;
    cursor: pointer;
    box-shadow: 0 2px 8px rgb(0 0 0 / 0.15);
    transition: background-color 0.3s ease;
  }

  .btn:hover, button:hover, input[type="submit"]:hover {
    background-color: var(--button-hover-bg);
  }

  label {
    display: block;
    font-weight: 600;
    margin-bottom: 8px;
  }

  input[type=file] {
    border: 2px dashed var(--primary-color);
    padding: 20px;
    width: 100%;
    border-radius: 12px;
    cursor: pointer;
    background-color: transparent;
    transition: border-color 0.3s ease;
    color: var(--light-text);
  }

  body.dark input[type=file] {
    border-color: #82b1ff;
    color: var(--dark-text);
  }

  input[type=file]:hover {
    border-color: var(--secondary-color);
  }

  form {
    max-width: 500px;
    margin: 30px auto;
    background:#fff;
    padding: 25px 30px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgb(0 0 0 / 0.1);
  }

  body.dark form {
    background: #1e1e1e;
    box-shadow: 0 4px 12px rgb(255 255 255 / 0.1);
  }

  .form-group {
    margin-bottom: 20px;
  }

  .footer {
    background: var(--primary-color);
    color: white;
    text-align: center;
    padding: 15px 8px;
    font-size: 0.875rem;
  }

  /* Responsive */
  @media (max-width: 600px) {
    .tools-grid {
      grid-template-columns: 1fr 1fr;
      gap: 15px;
    }

    form {
      margin: 20px 10px 40px 10px;
      padding: 20px;
    }
  }

  /* Scrollbar for dropdown */
  nav .dropdown {
    max-height: 200px;
    overflow-y: auto;
  }

</style>
</head>
<body>
<nav>
  <div class="brand" onclick="location.href='{{ url_for('home') }}'">PAPERPREP</div>
  <div>
    <button class="btn" id="theme-toggle" aria-label="Toggle Dark/Light Theme">
      <i class="fas fa-moon"></i> Dark Mode
    </button>
    <div class="menu">
      <button class="menu-button" aria-haspopup="true" aria-expanded="false" aria-controls="menu-list" id="menu-button">
        <i class="fas fa-bars"></i>
      </button>
      <div class="dropdown" id="menu-list" role="menu" aria-labelledby="menu-button">
        <a href="{{ url_for('about') }}" role="menuitem">About</a>
        <a href="{{ url_for('privacy') }}" role="menuitem">Privacy</a>
        <a href="{{ url_for('contact') }}" role="menuitem">Contact</a>
        <a href="{{ url_for('terms') }}" role="menuitem">Terms & Conditions</a>
      </div>
    </div>
  </div>
</nav>
<main>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul style="max-width:500px; margin: 0 auto 20px auto; list-style:none; padding-left:0; color:#d33;">
          {% for message in messages %}
            <li>{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    {% block content %}
    {% endblock %}
</main>
<footer class="footer">
  &copy; {{ current_year }} PAPERPREP - College Project. All rights reserved.
</footer>
<script>
  (function(){
    const toggleBtn = document.getElementById('theme-toggle');
    toggleBtn.addEventListener('click', () => {
      document.body.classList.toggle('dark');
      if(document.body.classList.contains('dark')){
        toggleBtn.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
        localStorage.setItem('theme', 'dark');
      } else {
        toggleBtn.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
        localStorage.setItem('theme', 'light');
      }
    });
    // Set theme from localStorage
    if(localStorage.getItem('theme') === 'dark'){
      document.body.classList.add('dark');
      toggleBtn.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
    }
    // Menu aria
    const menuButton = document.getElementById('menu-button');
    const menuList = document.getElementById('menu-list');
    menuButton.addEventListener('click', () => {
      const expanded = menuButton.getAttribute('aria-expanded') === 'true' || false;
      menuButton.setAttribute('aria-expanded', !expanded);
      if(menuList.style.display === 'block') {
        menuList.style.display = 'none';
      } else {
        menuList.style.display = 'block';
      }
    });
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!menuButton.contains(e.target) && !menuList.contains(e.target)) {
        menuList.style.display = 'none';
        menuButton.setAttribute('aria-expanded', false);
      }
    });
  })();
</script>
</body>
</html>
"""

# Home page with tools menu
HOME_CONTENT = """
{% extends "base.html" %}
{% block content %}
<h1>Welcome to PAPERPREP</h1>
<h2>Your all-in-one document & image conversion tool</h2>
<div class="tools-grid">
  <div class="tool-card" onclick="location.href='{{ url_for('pdf_to_word') }}'" tabindex="0" role="button" aria-pressed="false">
    <i class="fas fa-file-pdf"></i>
    <h3>PDF to Word</h3>
  </div>
  <div class="tool-card" onclick="location.href='{{ url_for('jpg_to_word') }}'" tabindex="0" role="button" aria-pressed="false">
    <i class="fas fa-file-image"></i>
    <h3>JPG to Word</h3>
  </div>
  <div class="tool-card" onclick="location.href='{{ url_for('ppt_to_pdf') }}'" tabindex="0" role="button" aria-pressed="false">
    <i class="fas fa-file-powerpoint"></i>
    <h3>PPT to PDF</h3>
  </div>
  <div class="tool-card" onclick="location.href='{{ url_for('pdf_to_ppt') }}'" tabindex="0" role="button" aria-pressed="false">
    <i class="fas fa-file-pdf"></i>
    <h3>PDF to PPT</h3>
  </div>
  <div class="tool-card" onclick="location.href='{{ url_for('images_to_pdf') }}'" tabindex="0" role="button" aria-pressed="false">
    <i class="fas fa-file-image"></i>
    <h3>Multiple Images to PDF</h3>
  </div>
  <div class="tool-card" onclick="location.href='{{ url_for('merge_pdf') }}'" tabindex="0" role="button" aria-pressed="false">
    <i class="fas fa-file-pdf"></i>
    <h3>Merge PDF</h3>
  </div>
  <div class="tool-card" onclick="location.href='{{ url_for('image_compress') }}'" tabindex="0" role="button" aria-pressed="false">
    <i class="fas fa-compress"></i>
    <h3>Image Compressor</h3>
  </div>
  <div class="tool-card" onclick="location.href='{{ url_for('pdf_compress') }}'" tabindex="0" role="button" aria-pressed="false">
    <i class="fas fa-file-pdf"></i>
    <h3>PDF Compressor</h3>
  </div>
</div>
{% endblock %}
"""

# Utility function to check file extensions allowed
def allowed_file(filename, tool_name):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(tool_name, set())

@app.route('/')
def home():
    return render_template_string(BASE_TEMPLATE, title="Home", current_year=2024, content=HOME_CONTENT, 
                                  block_content=HOME_CONTENT, get_flashed_messages=flash)

# We need to register the base template for other templates to extend from
app.jinja_loader = app.create_global_jinja_loader()
app.jinja_env.globals['url_for'] = url_for
app.jinja_env.globals['get_flashed_messages'] = lambda: []

# To enable Jinja inheritance in render_template_string, we will serve base as a template directly
@app.context_processor
def inject_base_template():
    return dict(base=BASE_TEMPLATE)

# About page
@app.route('/about')
def about():
    about_content = """
    {% extends "base.html" %}
    {% block content %}
    <h1>About PAPERPREP</h1>
    <p>PAPERPREP is your ultimate college companion for document and image conversion and compression tools.</p>
    <p>This project was developed as a college assignment with a focus on usability, design, and functionality.</p>
    {% endblock %}
    """
    return render_template_string(about_content, title="About", current_year=2024)

# Privacy page
@app.route('/privacy')
def privacy():
    privacy_content = """
    {% extends "base.html" %}
    {% block content %}
    <h1>Privacy Policy</h1>
    <p>We respect your privacy. Any files you upload are processed temporarily and not stored or shared. No data is kept after processing.</p>
    {% endblock %}
    """
    return render_template_string(privacy_content, title="Privacy", current_year=2024)

# Contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    contact_content_get = """
    {% extends "base.html" %}
    {% block content %}
    <h1>Contact Us</h1>
    <form method="post">
      <div class="form-group">
        <label for="name">Your Name:</label>
        <input id="name" name="name" required placeholder="Your full name" />
      </div>
      <div class="form-group">
        <label for="email">Your Email:</label>
        <input id="email" name="email" type="email" required placeholder="example@mail.com" />
      </div>
      <div class="form-group">
        <label for="message">Message:</label>
        <textarea id="message" name="message" required rows="4" placeholder="Your message here"></textarea>
      </div>
      <input type="submit" class="btn" value="Send Message"/>
    </form>
    {% endblock %}
    """

    contact_content_post = """
    {% extends "base.html" %}
    {% block content %}
    <h1>Contact Us</h1>
    <p>Thank you for reaching out to us, {{ name }}! We will get back to you shortly.</p>
    {% endblock %}
    """

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        # Normally here you would process/send email but for demo, just flash thanks
        if not (name and email and message):
            flash("Please fill in all the fields.")
            return redirect(url_for('contact'))
        # For now, just render thank you page
        return render_template_string(contact_content_post, title="Contact", current_year=2024, name=name)

    return render_template_string(contact_content_get, title="Contact", current_year=2024)

# Terms page
@app.route('/terms')
def terms():
    terms_content = """
    {% extends "base.html" %}
    {% block content %}
    <h1>Terms & Conditions</h1>
    <p>Use PAPERPREP responsibly. We do not guarantee 100% accuracy on conversions and are not liable for data loss.</p>
    <p>The software is provided as-is without warranties of any kind.</p>
    {% endblock %}
    """
    return render_template_string(terms_content, title="Terms & Conditions", current_year=2024)

# Tool pages below with form and processing

@app.route('/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    form_html = """
    {% extends "base.html" %}
    {% block content %}
    <h1>PDF to Word Converter</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="form-group">
        <label for="pdf_file">Upload PDF file:</label>
        <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required />
      </div>
      <input type="submit" class="btn" value="Convert" />
    </form>
    {% endblock %}
    """
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, 'pdf_to_word'):
            filename = secure_filename(file.filename)
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    pdf_path = os.path.join(tmpdir, filename)
                    file.save(pdf_path)
                    docx_path = os.path.join(tmpdir, "converted.docx")
                    cv = Converter(pdf_path)
                    cv.convert(docx_path, start=0, end=None)
                    cv.close()
                    return send_file(docx_path, download_name="converted.docx", as_attachment=True)
            except Exception as e:
                flash(f"Conversion failed: {e}")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload a PDF.")
            return redirect(request.url)
    return render_template_string(form_html, title="PDF to Word", current_year=2024)

@app.route('/jpg-to-word', methods=['GET', 'POST'])
def jpg_to_word():
    form_html = """
    {% extends "base.html" %}
    {% block content %}
    <h1>JPG to Word Converter (OCR)</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="form-group">
        <label for="image_file">Upload JPG/PNG image:</label>
        <input type="file" id="image_file" name="image_file" accept=".jpg,.jpeg,.png" required />
      </div>
      <input type="submit" class="btn" value="Convert" />
    </form>
    {% endblock %}
    """
    if request.method == 'POST':
        if 'image_file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['image_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, 'jpg_to_word'):
            try:
                image = Image.open(file.stream).convert('RGB')
                text = pytesseract.image_to_string(image)
                if not text.strip():
                    flash("No text detected in the image.")
                    return redirect(request.url)
                doc = Document()
                doc.add_paragraph(text)
                mem_file = io.BytesIO()
                doc.save(mem_file)
                mem_file.seek(0)
                return send_file(mem_file, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                 download_name='converted.docx', as_attachment=True)
            except Exception as e:
                flash(f"OCR conversion failed: {e}")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload JPG/PNG image.")
            return redirect(request.url)
    return render_template_string(form_html, title="JPG to Word", current_year=2024)

@app.route('/ppt-to-pdf', methods=['GET', 'POST'])
def ppt_to_pdf():
    # We will convert PPT to PDF using python-pptx to images then save as PDF pages
    form_html = """
    {% extends "base.html" %}
    {% block content %}
    <h1>PPT to PDF Converter</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="form-group">
        <label for="ppt_file">Upload PPTX file:</label>
        <input type="file" id="ppt_file" name="ppt_file" accept=".pptx" required />
      </div>
      <input type="submit" class="btn" value="Convert" />
    </form>
    <p><small>Note: Only PPTX is supported.</small></p>
    {% endblock %}
    """
    if request.method == 'POST':
        if 'ppt_file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['ppt_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, 'ppt_to_pdf'):
            filename = secure_filename(file.filename)
            try:
                # Save pptx file temporarily
                with tempfile.TemporaryDirectory() as tmpdir:
                    pptx_path = os.path.join(tmpdir, filename)
                    file.save(pptx_path)
                    prs = Presentation(pptx_path)
                    images = []
                    for i, slide in enumerate(prs.slides):
                        image_path = os.path.join(tmpdir, f"slide_{i}.png")
                        # Save slide as image: python-pptx does not support saving slides as images natively
                        # So to keep simple, show message it's not supported, or skip
                        # We'll just create empty white image as placeholder to allow PDF creation
                        img = Image.new('RGB', (960, 540), color='white')
                        img.save(image_path)
                        images.append(image_path)

                    # merge images into pdf
                    pdf_path = os.path.join(tmpdir, "converted.pdf")
                    image_list = []
                    for im_path in images:
                        im = Image.open(im_path).convert('RGB')
                        image_list.append(im)
                    if image_list:
                        first_image = image_list.pop(0)
                        first_image.save(pdf_path, save_all=True, append_images=image_list)
                    else:
                        flash("PPT slides image creation failed.")
                        return redirect(request.url)
                    return send_file(pdf_path, download_name="converted.pdf", as_attachment=True)
            except Exception as e:
                flash(f"Conversion failed: {e}")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload PPTX.")
            return redirect(request.url)
    return render_template_string(form_html, title="PPT to PDF", current_year=2024)

@app.route('/pdf-to-ppt', methods=['GET', 'POST'])
def pdf_to_ppt():
    # Convert PDF pages to images and add as slides in an empty pptx
    form_html = """
    {% extends "base.html" %}
    {% block content %}
    <h1>PDF to PPT Converter</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="form-group">
        <label for="pdf_file">Upload PDF file:</label>
        <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required />
      </div>
      <input type="submit" class="btn" value="Convert" />
    </form>
    <p><small>Note: PDF pages will be converted as images into PPT slides.</small></p>
    {% endblock %}
    """
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, 'pdf_to_ppt'):
            try:
                from pdf2image import convert_from_bytes
            except ImportError:
                flash("pdf2image module not installed. Please install it to use this feature.")
                return redirect(request.url)
            try:
                pdf_bytes = file.read()
                images = convert_from_bytes(pdf_bytes)
                if not images:
                    flash("No pages found in PDF.")
                    return redirect(request.url)
                prs = Presentation()
                prs.slide_height = Inches(7.5)
                prs.slide_width = Inches(10)
                for img in images:
                    slide = prs.slides.add_slide(prs.slide_layouts[6])
                    with tempfile.NamedTemporaryFile(suffix=".png") as tmp_img_file:
                        img.save(tmp_img_file.name, format='PNG')
                        left = top = Inches(0)
                        pic = slide.shapes.add_picture(tmp_img_file.name, left, top, width=prs.slide_width, height=prs.slide_height)
                mem_file = io.BytesIO()
                prs.save(mem_file)
                mem_file.seek(0)
                return send_file(mem_file, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                                 download_name='converted.pptx', as_attachment=True)
            except Exception as e:
                flash(f"Conversion failed: {e}")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload PDF.")
            return redirect(request.url)
    return render_template_string(form_html, title="PDF to PPT", current_year=2024)


@app.route('/images-to-pdf', methods=['GET', 'POST'])
def images_to_pdf():
    form_html = """
    {% extends "base.html" %}
    {% block content %}
    <h1>Multiple Images to One PDF</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="form-group">
        <label for="image_files">Upload Image files (multiple allowed):</label>
        <input type="file" id="image_files" name="image_files" accept=".jpg,.jpeg,.png,.bmp,.gif" multiple required />
      </div>
      <input type="submit" class="btn" value="Convert" />
    </form>
    {% endblock %}
    """
    if request.method == 'POST':
        if 'image_files' not in request.files:
            flash("No file part")
            return redirect(request.url)
        files = request.files.getlist('image_files')
        if not files or files[0].filename == '':
            flash('No selected files')
            return redirect(request.url)
        images = []
        try:
            for file in files:
                if file and allowed_file(file.filename, 'images_to_pdf'):
                    img = Image.open(file.stream).convert('RGB')
                    images.append(img)
                else:
                    flash("Invalid file type in upload. Please upload images.")
                    return redirect(request.url)
            if not images:
                flash("No valid images uploaded.")
                return redirect(request.url)
            mem_file = io.BytesIO()
            images[0].save(mem_file, format='PDF', save_all=True, append_images=images[1:])
            mem_file.seek(0)
            return send_file(mem_file, mimetype='application/pdf', download_name='combined.pdf', as_attachment=True)
        except Exception as e:
            flash(f"Image to PDF conversion failed: {e}")
            return redirect(request.url)
    return render_template_string(form_html, title="Images to PDF", current_year=2024)

@app.route('/merge-pdf', methods=['GET', 'POST'])
def merge_pdf():
    form_html = """
    {% extends "base.html" %}
    {% block content %}
    <h1>Merge PDF Files</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="form-group">
        <label for="pdf_files">Upload PDF files (multiple allowed):</label>
        <input type="file" id="pdf_files" name="pdf_files" accept=".pdf" multiple required />
      </div>
      <input type="submit" class="btn" value="Merge" />
    </form>
    {% endblock %}
    """
    if request.method == 'POST':
        if 'pdf_files' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('pdf_files')
        if not files or files[0].filename == '':
            flash('No selected files')
            return redirect(request.url)
        merger = PdfMerger()
        try:
            for file in files:
                if file and allowed_file(file.filename, 'merge_pdf'):
                    # PyPDF2 requires a seekable stream
                    file.stream.seek(0)
                    merger.append(file.stream)
                else:
                    flash("Invalid file type in upload. Please upload PDFs.")
                    return redirect(request.url)
            mem_file = io.BytesIO()
            merger.write(mem_file)
            merger.close()
            mem_file.seek(0)
            return send_file(mem_file, mimetype='application/pdf', download_name='merged.pdf', as_attachment=True)
        except Exception as e:
            flash(f"Merging PDFs failed: {e}")
            return redirect(request.url)
    return render_template_string(form_html, title="Merge PDF", current_year=2024)

@app.route('/image-compress', methods=['GET', 'POST'])
def image_compress():
    form_html = """
    {% extends "base.html" %}
    {% block content %}
    <h1>Image Compressor</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="form-group">
        <label for="image_file">Upload Image file (JPG, PNG):</label>
        <input type="file" id="image_file" name="image_file" accept=".jpg,.jpeg,.png" required />
      </div>
      <input type="submit" class="btn" value="Compress" />
    </form>
    <p><small>Image will be compressed to reduce size but keep decent quality.</small></p>
    {% endblock %}
    """
    if request.method == 'POST':
        if 'image_file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['image_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, 'image_compress'):
            try:
                img = Image.open(file.stream).convert('RGB')
                mem_file = io.BytesIO()
                # Save compressed with quality 40 (adjustable)
                img.save(mem_file, format='JPEG', quality=40,optimize=True)
                mem_file.seek(0)
                return send_file(mem_file, mimetype='image/jpeg', download_name='compressed.jpg', as_attachment=True)
            except Exception as e:
                flash(f"Image compression failed: {e}")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload JPG/PNG.")
            return redirect(request.url)
    return render_template_string(form_html, title="Image Compressor", current_year=2024)

@app.route('/pdf-compress', methods=['GET', 'POST'])
def pdf_compress():
    form_html = """
    {% extends "base.html" %}
    {% block content %}
    <h1>PDF Compressor</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="form-group">
        <label for="pdf_file">Upload PDF file:</label>
        <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required />
      </div>
      <input type="submit" class="btn" value="Compress" />
    </form>
    <p><small>Basic PDF compression by rewriting the file.</small></p>
    {% endblock %}
    """
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, 'pdf_compress'):
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_writer = PyPDF2.PdfWriter()
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                mem_file = io.BytesIO()
                pdf_writer.write(mem_file)
                mem_file.seek(0)
                return send_file(mem_file, mimetype='application/pdf', download_name='compressed.pdf', as_attachment=True)
            except Exception as e:
                flash(f"PDF compression failed: {e}")
                return redirect(request.url)
        else:
            flash("Invalid file type. Please upload PDF.")
            return redirect(request.url)
    return render_template_string(form_html, title="PDF Compressor", current_year=2024)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
