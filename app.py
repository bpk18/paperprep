import os
import tempfile
import shutil
from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader
from PIL import Image
from pdf2docx import Converter
from docx import Document
from io import BytesIO
from docx.shared import Inches

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # for flashing messages

# Ensure temp directory
TEMP_DIR = tempfile.mkdtemp()

# Allowed extensions for tools
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif'}
ALLOWED_PDF = {'pdf'}
ALLOWED_PPT = {'ppt', 'pptx'}
ALLOWED_DOCX = {'docx'}

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


base_html = '''
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PAPERPREP - {{ title }}</title>
    <meta name="description" content="PAPERPREP: Your futuristic document and image conversion toolkit. Convert PDFs, Word, Images, and more with ease. Mobile responsive, modern UI." />
    <meta name="keywords" content="PDF to Word, JPG to Word, PPT to PDF, PDF to PPT, Image to PDF, Merge PDF, Compress PDF, Compress Image, Document Converter" />
    <meta name="author" content="PAPERPREP" />
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon" />
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9764517671001230" crossorigin="anonymous"></script>
    <style>
        /* Reset and base */
        *, *::before, *::after {
          box-sizing: border-box;
        }
        body {
          margin: 0;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background-color: var(--bg);
          color: var(--text);
          transition: background-color 0.3s, color 0.3s;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }
        a {
          color: var(--primary);
          text-decoration: none;
        }
        a:hover {
          text-decoration: underline;
        }
        /* Light theme variables */
        :root {
          --bg: #f3f7ff;
          --text: #1a1a1a;
          --primary: #3f51b5;
          --secondary: #7986cb;
          --card-bg: #ffffff;
          --card-shadow: rgba(63, 81, 181, 0.15);
          --btn-bg: #3f51b5;
          --btn-text: #ffffff;
          --btn-hover-bg: #2c3e9e;
          --nav-bg: #ffffff;
          --nav-text: #1a1a1a;
          --border-color: #d1d9ff;
        }
        /* Dark theme variables */
        [data-theme="dark"] {
          --bg: #121217;
          --text: #e4e6eb;
          --primary: #8ab4f8;
          --secondary: #3c4048;
          --card-bg: #1c1c28;
          --card-shadow: rgba(139, 170, 255, 0.3);
          --btn-bg: #8ab4f8;
          --btn-text: #121217;
          --btn-hover-bg: #6890f1;
          --nav-bg: #1c1c28;
          --nav-text: #e4e6eb;
          --border-color: #333849;
        }

        /* Navbar Styles */
        nav {
          background: var(--nav-bg);
          color: var(--nav-text);
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.7rem 1.5rem;
          box-shadow: 0 2px 4px var(--card-shadow);
          position: sticky;
          top: 0;
          z-index: 1000;
        }
        .navbar-brand {
          font-weight: 900;
          font-size: 1.5rem;
          letter-spacing: 3px;
          color: var(--primary);
          user-select: none;
        }
        .nav-links {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .nav-links a {
          font-weight: 600;
          font-size: 1rem;
          padding: 0.3rem 0.6rem;
          border-radius: 5px;
          transition: background-color 0.3s;
        }
        .nav-links a:hover,
        .nav-links a:focus {
          background-color: var(--secondary);
          color: var(--btn-text);
          outline: none;
        }
        /* Hamburger menu */
        .menu-toggle {
          display: none;
          flex-direction: column;
          justify-content: space-around;
          width: 25px;
          height: 22px;
          cursor: pointer;
        }
        .menu-toggle span {
          width: 100%;
          height: 3px;
          background: var(--nav-text);
          border-radius: 5px;
          transition: all 0.3s;
        }

        /* Mobile nav toggle */
        #nav-checkbox {
          display: none;
        }
        #nav-checkbox:checked ~ .nav-links {
          display: flex;
          flex-direction: column;
          position: absolute;
          top: 60px;
          left: 0;
          right: 0;
          background: var(--nav-bg);
          padding: 1rem 0;
          border-top: 1px solid var(--border-color);
          box-shadow: 0 6px 10px var(--card-shadow);
          z-index: 999;
        }
        @media (max-width: 768px) {
          .nav-links {
            display: none;
            width: 100%;
          }
          .menu-toggle {
            display: flex;
          }
        }

        /* Main content */
        main {
          flex-grow: 1;
          padding: 1.5rem 1rem 3rem;
          max-width: 900px;
          margin: auto;
          width: 100%;
        }

        /* Footer */
        footer {
          background: var(--nav-bg);
          color: var(--nav-text);
          text-align: center;
          padding: 1rem;
          font-size: 0.9rem;
          border-top: 1px solid var(--border-color);
          user-select: none;
        }

        /* Tool Cards Grid */
        .tools-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 1.5rem;
          max-width: 1000px;
          margin: 0 auto 2rem;
        }
        .tool-card {
          background: var(--card-bg);
          border-radius: 12px;
          box-shadow: 0 4px 14px var(--card-shadow);
          padding: 1.4rem 1.2rem;
          text-align: center;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          transition: transform 0.3s ease;
          user-select: none;
        }
        .tool-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 30px var(--card-shadow);
        }
        .tool-icon {
          width: 60px;
          height: 60px;
          margin: 0 auto 1rem;
          fill: var(--primary);
          transition: fill 0.3s;
        }
        .tool-name {
          font-size: 1.2rem;
          font-weight: 700;
          margin-bottom: 1rem;
          color: var(--text);
        }
        .btn {
          background-color: var(--btn-bg);
          color: var(--btn-text);
          border: none;
          border-radius: 30px;
          cursor: pointer;
          padding: 0.5rem 1.8rem;
          font-weight: 700;
          letter-spacing: 1px;
          box-shadow: 0 4px 10px var(--card-shadow);
          transition: background-color 0.3s ease;
          user-select: none;
        }
        .btn:hover {
          background-color: var(--btn-hover-bg);
        }

        /* Toggle Button */
        .theme-toggle-btn {
          background: transparent;
          border: 2px solid var(--primary);
          border-radius: 30px;
          cursor: pointer;
          padding: 0.3rem 1rem;
          font-weight: 600;
          color: var(--primary);
          transition: background-color 0.3s, color 0.3s;
          user-select: none;
        }
        .theme-toggle-btn:hover {
          background-color: var(--primary);
          color: var(--btn-text);
        }

        /* Responsive Typography */
        h1 {
          font-size: 2.5rem;
          text-align: center;
          margin-bottom: 1rem;
          user-select: none;
          color: var(--primary);
        }
        p.lead {
          font-size: 1.1rem;
          text-align: center;
          margin-bottom: 1.8rem;
          max-width: 700px;
          margin-left: auto;
          margin-right: auto;
          user-select: none;
        }

        /* Form styles for contact and tools */
        form {
          max-width: 500px;
          margin: 0 auto 2rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        label {
          font-weight: 600;
          margin-bottom: 0.3rem;
          user-select: none;
          color: var(--text);
        }
        input[type="file"], input[type="text"], input[type="email"], textarea {
          padding: 0.5rem 0.8rem;
          border-radius: 8px;
          border: 1px solid var(--border-color);
          font-size: 1rem;
          background-color: var(--card-bg);
          color: var(--text);
          resize: vertical;
          transition: border-color 0.3s;
        }
        input[type="file"]:focus, input[type="text"]:focus, input[type="email"]:focus, textarea:focus {
          border-color: var(--primary);
          outline: none;
        }
        textarea {
          min-height: 100px;
        }
        input[type="submit"] {
          width: fit-content;
          align-self: center;
          padding: 0.6rem 2rem;
          background-color: var(--btn-bg);
          color: var(--btn-text);
          border: none;
          border-radius: 30px;
          cursor: pointer;
          font-weight: 700;
          box-shadow: 0 4px 10px var(--card-shadow);
          transition: background-color 0.3s ease;
          user-select: none;
        }
        input[type="submit"]:hover {
          background-color: var(--btn-hover-bg);
        }

        /* Flash messages */
        .flash {
          max-width: 500px;
          margin: 0 auto 1.5rem;
          padding: 1rem;
          background-color: #f44336;
          color: white;
          border-radius: 8px;
          text-align: center;
        }

        /* Result download link */
        .result-link {
          display: flex;
          justify-content: center;
          margin-bottom: 2rem;
        }
        .result-link a {
          font-weight: 700;
          background-color: var(--primary);
          color: var(--btn-text);
          padding: 0.6rem 1.5rem;
          border-radius: 25px;
          text-decoration: none;
          box-shadow: 0 4px 10px var(--card-shadow);
          transition: background-color 0.3s ease;
        }
        .result-link a:hover {
          background-color: var(--btn-hover-bg);
        }

        /* Scroll locking when menu open */
        body.menu-open {
          overflow: hidden;
        }
    </style>
</head>
<body>
    <nav role="navigation" aria-label="Primary Navigation">
        <div class="navbar-brand" tabindex="0">PAPERPREP</div>
        <input type="checkbox" id="nav-checkbox" aria-label="Toggle menu" />
        <label for="nav-checkbox" class="menu-toggle" tabindex="0" aria-controls="nav-links" aria-expanded="false" aria-haspopup="true">
            <span></span>
            <span></span>
            <span></span>
        </label>
        <div class="nav-links" id="nav-links" role="menu" aria-labelledby="nav-checkbox">
            <a href="{{ url_for('about') }}" role="menuitem" tabindex="0">About</a>
            <a href="{{ url_for('privacy') }}" role="menuitem" tabindex="0">Privacy</a>
            <a href="{{ url_for('contact') }}" role="menuitem" tabindex="0">Contact</a>
            <a href="{{ url_for('terms') }}" role="menuitem" tabindex="0">Terms &amp; Conditions</a>
            <a href="{{ url_for('home') }}" role="menuitem" tabindex="0">Home</a>
        </div>
        <button class="theme-toggle-btn" id="theme-toggle" aria-label="Toggle dark/light theme">Dark Theme</button>
    </nav>
    <main>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
            <div class="flash" role="alert">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </main>
    <footer role="contentinfo">
        &copy; 2024 PAPERPREP - All rights reserved.
    </footer>
    <script>
        // Theme toggle
        const btn = document.getElementById('theme-toggle');
        const htmlEl = document.documentElement;

        // Load saved theme or default light
        let currentTheme = localStorage.getItem('theme') || 'light';
        htmlEl.setAttribute('data-theme', currentTheme);
        btn.textContent = currentTheme === 'light' ? 'Dark Theme' : 'Light Theme';

        btn.addEventListener('click', () => {
            if (htmlEl.getAttribute('data-theme') === 'light') {
                htmlEl.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                btn.textContent = 'Light Theme';
            } else {
                htmlEl.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                btn.textContent = 'Dark Theme';
            }
        });

        // Accessibility: close nav menu on link click
        const navCheckbox = document.getElementById('nav-checkbox');
        const navLinks = document.querySelectorAll('.nav-links a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navCheckbox.checked) {
                    navCheckbox.checked = false;
                }
            });
        });
    </script>
</body>
</html>
'''

# Home page with links to tool pages
home_html = '''
{% extends 'base.html' %}
{% block content %}
    <h1>Welcome to PAPERPREP</h1>
    <p class="lead">Your all-in-one document and image conversion toolkit with a futuristic UI and seamless experience.</p>
    <section class="tools-grid" aria-label="Conversion Tools">

        <article class="tool-card">
            <div class="tool-name">PDF to Word</div>
            <a class="btn" href="{{ url_for('pdf_to_word') }}">Open</a>
        </article>

        <article class="tool-card">
            <div class="tool-name">JPG to Word</div>
            <a class="btn" href="{{ url_for('jpg_to_word') }}">Open</a>
        </article>

        <article class="tool-card">
            <div class="tool-name">PPT to PDF</div>
            <a class="btn" href="{{ url_for('ppt_to_pdf') }}">Open</a>
        </article>

        <article class="tool-card">
            <div class="tool-name">PDF to PPT</div>
            <a class="btn" href="{{ url_for('pdf_to_ppt') }}">Open</a>
        </article>

        <article class="tool-card">
            <div class="tool-name">Images to PDF</div>
            <a class="btn" href="{{ url_for('images_to_pdf') }}">Open</a>
        </article>

        <article class="tool-card">
            <div class="tool-name">Merge PDF</div>
            <a class="btn" href="{{ url_for('merge_pdf') }}">Open</a>
        </article>

        <article class="tool-card">
            <div class="tool-name">Image Compressor</div>
            <a class="btn" href="{{ url_for('image_compressor') }}">Open</a>
        </article>

        <article class="tool-card">
            <div class="tool-name">PDF Compressor</div>
            <a class="btn" href="{{ url_for('pdf_compressor') }}">Open</a>
        </article>
    </section>
{% endblock %}
'''

generic_tool_html = '''
{% extends 'base.html' %}
{% block content %}
    <h1>{{ title }}</h1>
    <p class="lead">{{ description }}</p>

    {% if result_fileurl %}
        <div class="result-link">
            <a href="{{ result_fileurl }}" download="{{ result_filename }}">Download {{ title }} Result</a>
        </div>
    {% endif %}

    <form method="post" enctype="multipart/form-data">
        {% for field in fields %}
            <label for="{{ field.id }}">{{ field.label }}</label>
            <input
              type="{{ field.type }}"
              name="{{ field.name }}"{% if field.multiple %} multiple{% endif %}
              id="{{ field.id }}"{% if field.accept %} accept="{{ field.accept }}"{% endif %}
              required="{{ 'required' if field.required else '' }}"
            />
        {% endfor %}
        <input type="submit" value="Convert" />
    </form>
{% endblock %}
'''

# About, Privacy, Contact, Terms templates - reuse from before but with minor adjustments
about_html = '''
{% extends 'base.html' %}
{% block content %}
    <h1>About PAPERPREP</h1>
    <p class="lead">
        PAPERPREP is your futuristic document and image conversion hub, designed to simplify your workflow.
        With a clean, sleek UI and powerful tools, we help you transform your files seamlessly on any device.
    </p>
{% endblock %}
'''

privacy_html = '''
{% extends 'base.html' %}
{% block content %}
    <h1>Privacy Policy</h1>
    <p>
      We value your privacy. PAPERPREP does not store any files you upload or any personal data. All file processing is done securely and temporarily.
    </p>
    <p>
      By using PAPERPREP, you agree to our processing guidelines and terms.
    </p>
{% endblock %}
'''

contact_html = '''
{% extends 'base.html' %}
{% block content %}
    <h1>Contact Us</h1>
    <p class="lead">Have questions or feedback? Reach out to us!</p>
    <form id="contact-form" onsubmit="event.preventDefault(); alert('Thank you for contacting us! We will get back to you soon.'); this.reset();">
        <label for="name">Name</label>
        <input type="text" id="name" name="name" placeholder="Your full name" required />
        
        <label for="email">Email</label>
        <input type="email" id="email" name="email" placeholder="your.email@example.com" required />
        
        <label for="message">Message</label>
        <textarea id="message" name="message" placeholder="Write your message here..." required></textarea>
        
        <input type="submit" value="Send Message" />
    </form>
{% endblock %}
'''

terms_html = '''
{% extends 'base.html' %}
{% block content %}
    <h1>Terms &amp; Conditions</h1>
    <p>
      By using PAPERPREP, you agree to use the platform responsibly.
      We provide conversion tools as-is without warranties.
      You are responsible for your files and usage.
    </p>
    <p>
      PAPERPREP reserves the right to modify these terms at any time.
    </p>
{% endblock %}
'''

# Register the templates
from jinja2 import DictLoader
app.jinja_loader = DictLoader({
    'base.html': base_html,
    'home.html': home_html,
    'generic_tool.html': generic_tool_html,
    'about.html': about_html,
    'privacy.html': privacy_html,
    'contact.html': contact_html,
    'terms.html': terms_html,
})

@app.route('/')
def home():
    return render_template_string(home_html, title="Home")

@app.route('/about')
def about():
    return render_template_string(about_html, title="About")

@app.route('/privacy')
def privacy():
    return render_template_string(privacy_html, title="Privacy Policy")

@app.route('/contact')
def contact():
    return render_template_string(contact_html, title="Contact")

@app.route('/terms')
def terms():
    return render_template_string(terms_html, title="Terms & Conditions")


# Tool: PDF to Word
@app.route('/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    title = "PDF to Word"
    description = "Convert your PDF documents to editable Word files (.docx)."
    result_fileurl = None
    result_filename = None

    fields = [
        {"id": "pdf_file", "name": "pdf_file", "label": "Upload PDF file", "type": "file", "accept": ".pdf", "multiple": False, "required": True}
    ]

    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_PDF):
            filename = secure_filename(file.filename)
            input_path = os.path.join(TEMP_DIR, filename)
            file.save(input_path)
            
            # Output file
            output_filename = os.path.splitext(filename)[0] + '.docx'
            output_path = os.path.join(TEMP_DIR, output_filename)
            
            try:
                cv = Converter(input_path)
                cv.convert(output_path, start=0, end=None)
                cv.close()
                return send_file(output_path, as_attachment=True, download_name=output_filename)
            except Exception as e:
                flash(f'Conversion failed: {e}')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a PDF file.')
            return redirect(request.url)
    return render_template_string(generic_tool_html, title=title, description=description, fields=fields, result_fileurl=result_fileurl, result_filename=result_filename)


# Tool: JPG to Word (simple create docx with embedded image)
@app.route('/jpg-to-word', methods=['GET', 'POST'])
def jpg_to_word():
    title = "JPG to Word"
    description = "Convert JPG or other image files into a Word document with the image embedded."
    result_fileurl = None
    result_filename = None

    fields = [
        {"id": "image_file", "name": "image_file", "label": "Upload Image file", "type": "file", "accept": "image/*", "multiple": False, "required": True}
    ]

    if request.method == 'POST':
        if 'image_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = secure_filename(file.filename)
            input_path = os.path.join(TEMP_DIR, filename)
            file.save(input_path)
            
            output_filename = os.path.splitext(filename)[0] + '.docx'
            output_path = os.path.join(TEMP_DIR, output_filename)
            
            try:
                doc = Document()
                doc.add_paragraph("Image embedded below:")
                doc.add_picture(input_path, width=docx.shared.Inches(5))
                doc.save(output_path)
                return send_file(output_path, as_attachment=True, download_name=output_filename)
            except Exception as e:
                flash(f'Conversion failed: {e}')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload an image file.')
            return redirect(request.url)
    return render_template_string(generic_tool_html, title=title, description=description, fields=fields, result_fileurl=result_fileurl, result_filename=result_filename)


# Tool: PPT to PDF (for simplicity, just reject, as no easy pure python conversion without libreoffice or external tools)
@app.route('/ppt-to-pdf', methods=['GET', 'POST'])
def ppt_to_pdf():
    title = "PPT to PDF"
    description = "Convert your PowerPoint files (.ppt, .pptx) to PDF. (NOTE: Requires external tool to fully support)"
    result_fileurl = None
    result_filename = None

    fields = [
        {"id": "ppt_file", "name": "ppt_file", "label": "Upload PPT/PPTX file", "type": "file", "accept": ".ppt,.pptx", "multiple": False, "required": True}
    ]

    if request.method == 'POST':
        flash('PPT to PDF conversion requires external tools (LibreOffice). This feature is coming soon.')
        return redirect(request.url)

    return render_template_string(generic_tool_html, title=title, description=description, fields=fields, result_fileurl=result_fileurl, result_filename=result_filename)


# Tool: PDF to PPT (placeholder, no direct conversion implemented)
@app.route('/pdf-to-ppt', methods=['GET', 'POST'])
def pdf_to_ppt():
    title = "PDF to PPT"
    description = "Convert PDF to PowerPoint (PPT) files. (Feature coming soon)"
    result_fileurl = None
    result_filename = None

    fields = [
        {"id": "pdf_file", "name": "pdf_file", "label": "Upload PDF file", "type": "file", "accept": ".pdf", "multiple": False, "required": True}
    ]

    if request.method == 'POST':
        flash('PDF to PPT conversion feature will be added soon!')
        return redirect(request.url)

    return render_template_string(generic_tool_html, title=title, description=description, fields=fields, result_fileurl=result_fileurl, result_filename=result_filename)


# Tool: Multiple images to one PDF
@app.route('/images-to-pdf', methods=['GET', 'POST'])
def images_to_pdf():
    title = "Images to PDF"
    description = "Combine multiple image files into a single PDF document."
    result_fileurl = None
    result_filename = None

    fields = [
        {"id": "images", "name": "images", "label": "Upload Image files", "type": "file", "accept": "image/*", "multiple": True, "required": True}
    ]

    if request.method == 'POST':
        files = request.files.getlist('images')
        if not files or len(files) == 0:
            flash('No files selected')
            return redirect(request.url)
        image_files = []
        try:
            for file in files:
                if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    filename = secure_filename(file.filename)
                    path = os.path.join(TEMP_DIR, filename)
                    file.save(path)
                    image_files.append(path)
                else:
                    flash('Invalid file in selection. Please upload images only.')
                    return redirect(request.url)
            if not image_files:
                flash('No valid image files found.')
                return redirect(request.url)
            
            images = [Image.open(img).convert('RGB') for img in image_files]
            output_path = os.path.join(TEMP_DIR, "combined_images.pdf")
            images[0].save(output_path, save_all=True, append_images=images[1:])
            return send_file(output_path, as_attachment=True, download_name="combined_images.pdf")
        except Exception as e:
            flash(f'Error during conversion: {e}')
            return redirect(request.url)

    return render_template_string(generic_tool_html, title=title, description=description, fields=fields, result_fileurl=result_fileurl, result_filename=result_filename)


# Tool: Merge PDF
@app.route('/merge-pdf', methods=['GET', 'POST'])
def merge_pdf():
    title = "Merge PDF"
    description = "Merge multiple PDF files into one unified PDF document."
    result_fileurl = None
    result_filename = None

    fields = [
        {"id": "pdfs", "name": "pdfs", "label": "Upload PDF files", "type": "file", "accept": ".pdf", "multiple": True, "required": True}
    ]

    if request.method == 'POST':
        files = request.files.getlist('pdfs')
        if not files or len(files) == 0:
            flash('No files selected')
            return redirect(request.url)
        pdf_paths = []
        try:
            for file in files:
                if file and allowed_file(file.filename, ALLOWED_PDF):
                    filename = secure_filename(file.filename)
                    path = os.path.join(TEMP_DIR, filename)
                    file.save(path)
                    pdf_paths.append(path)
                else:
                    flash('Invalid file in selection. Please upload PDFs only.')
                    return redirect(request.url)
            if not pdf_paths:
                flash('No valid PDF files found.')
                return redirect(request.url)
            
            merger = PdfMerger()
            for pdf in pdf_paths:
                merger.append(pdf)
            output_path = os.path.join(TEMP_DIR, "merged.pdf")
            merger.write(output_path)
            merger.close()
            return send_file(output_path, as_attachment=True, download_name="merged.pdf")
        except Exception as e:
            flash(f'Error during merge: {e}')
            return redirect(request.url)

    return render_template_string(generic_tool_html, title=title, description=description, fields=fields, result_fileurl=result_fileurl, result_filename=result_filename)


# Tool: Image compressor (lower quality JPEG)
@app.route('/image-compressor', methods=['GET', 'POST'])
def image_compressor():
    title = "Image Compressor"
    description = "Compress images by lowering quality without significant loss."
    result_fileurl = None
    result_filename = None

    fields = [
        {"id": "image_file", "name": "image_file", "label": "Upload image file", "type": "file", "accept": "image/*", "multiple": False, "required": True}
    ]

    if request.method == 'POST':
        if 'image_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = secure_filename(file.filename)
            input_path = os.path.join(TEMP_DIR, filename)
            file.save(input_path)
            output_filename = f"compressed_{filename}"
            output_path = os.path.join(TEMP_DIR, output_filename)
            try:
                img = Image.open(input_path)
                img.save(output_path, optimize=True, quality=30)
                return send_file(output_path, as_attachment=True, download_name=output_filename)
            except Exception as e:
                flash(f'Compression failed: {e}')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload an image file.')
            return redirect(request.url)

    return render_template_string(generic_tool_html, title=title, description=description, fields=fields, result_fileurl=result_fileurl, result_filename=result_filename)


# Tool: PDF Compressor (basic, recreate PDF with PyPDF2 - limited compression capability)
@app.route('/pdf-compressor', methods=['GET', 'POST'])
def pdf_compressor():
    title = "PDF Compressor"
    description = "Basic PDF compression by rewriting the PDF file. (Advanced compression may not be available)"
    result_fileurl = None
    result_filename = None

    fields = [
        {"id": "pdf_file", "name": "pdf_file", "label": "Upload PDF file", "type": "file", "accept": ".pdf", "multiple": False, "required": True}
    ]

    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_PDF):
            filename = secure_filename(file.filename)
            input_path = os.path.join(TEMP_DIR, filename)
            file.save(input_path)
            output_filename = f"compressed_{filename}"
            output_path = os.path.join(TEMP_DIR, output_filename)
            try:
                reader = PdfReader(input_path)
                from PyPDF2 import PdfWriter
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                with open(output_path, 'wb') as fout:
                    writer.write(fout)
                return send_file(output_path, as_attachment=True, download_name=output_filename)
            except Exception as e:
                flash(f'Compression failed: {e}')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a PDF file.')
            return redirect(request.url)

    return render_template_string(generic_tool_html, title=title, description=description, fields=fields, result_fileurl=result_fileurl, result_filename=result_filename)


# Serve favicon.ico from static folder
@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')


if __name__ == '__main__':
    # Run on all interfaces port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)

