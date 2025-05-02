from flask import Flask, request, send_file, redirect, url_for, flash, get_flashed_messages
from werkzeug.utils import secure_filename
import os
import io
import tempfile
from datetime import datetime

from PIL import Image
import pytesseract
from docx import Document
from pdf2docx import Converter
from pptx import Presentation
from pptx.util import Inches
import PyPDF2

try:
    from pdf2image import convert_from_bytes
except ImportError:
    convert_from_bytes = None

app = Flask(__name__)
app.secret_key = "replace-with-your-secret-key"

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

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{{ title }}</title>
<meta name="description" content="PAPERPREP is your all-in-one file converter for PDFs, Word documents, images, and more. Fast, free, and easy to use." />
<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}" />
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet"/>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "PAPERPREP - All-in-One File Converter",
  "url": "https://paperprep.space",
  "description": "PAPERPREP is your all-in-one file converter for PDFs, Word documents, images, and more. Fast, free, and easy to use."
}
</script>

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
  /* Added to align theme toggle and menu button horizontally */
  nav > div {
    display: flex;
    align-items: center;
    gap: 10px;
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
    box-shadow: 0 3px 12px
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

  input[type=file], textarea, input[type=text], input[type=email] {
    border: 2px dashed var(--primary-color);
    padding: 10px;
    width: 100%;
    border-radius: 12px;
    cursor: pointer;
    background-color: transparent;
    transition: border-color 0.3s ease;
    color: var(--light-text);
    font-size: 1rem;
  }

  body.dark input[type=file], body.dark textarea, body.dark input[type=text], body.dark input[type=email] {
    border-color: #82b1ff;
    color: var(--dark-text);
  }

  input[type=file]:hover, textarea:hover, input[type=text]:hover, input[type=email]:hover {
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
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9764517671001230" crossorigin="anonymous"></script>
</head>
<body>
<nav>
  <div class="brand" onclick="location.href='{{ url_for('home') }}'">PAPERPREP</div>
  <div>
    <button class="btn" id="theme-toggle" aria-label="Toggle Dark/Light Theme">
      <i class="fas fa-moon"></i>
    </button>
    <div class="menu">
      <button class="menu-button" aria-haspopup="true" aria-expanded="false" aria-controls="menu-list" id="menu-button" aria-label="Menu">
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
  {{ content|safe }}
</main>
<footer class="footer">
  &copy; {{ year }} PAPERPREP . All rights reserved.
</footer>
<script>
  (function(){
    const toggleBtn = document.getElementById('theme-toggle');
    toggleBtn.addEventListener('click', () => {
      document.body.classList.toggle('dark');
      if(document.body.classList.contains('dark')){
        toggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
        localStorage.setItem('theme', 'dark');
      } else {
        toggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
        localStorage.setItem('theme', 'light');
      }
    });
    if(localStorage.getItem('theme') === 'dark'){
      document.body.classList.add('dark');
      toggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
    }
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

def allowed_file(filename, tool_name):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(tool_name, set())


def render_page(title, content_html, description=None, keywords=None):
    base_html = BASE_HTML.replace("{{ title }}", title)
    base_html = base_html.replace("{{ year }}", str(datetime.now().year))
    base_html = base_html.replace("{{ content|safe }}", content_html)

    if description:
        description_meta = f'<meta name="description" content=" Convert PDF, Word, Images, PPT, and more with PAPERPREP – the all-in-one file conversion toolkit. Fast, free, and easy to use." />'
        # Insert after the existing description tag, or create one if it doesn't exist
        if '<meta name="description"' in base_html:
            base_html = base_html.replace('<meta name="description" content="Convert PDF, Word, Images, PPT, and more with PAPERPREP – the all-in-one file conversion toolkit. Fast, free, and easy to use." />', description_meta)
        else:
            base_html = base_html.replace('</title>', f'</title>\n    {"PAPERPREP - Convert PDFs, Images & More"}')

    if keywords:
        keywords_meta = f'<meta name="keywords" content="file converter, PAPERPREP, PDF tools, PDF to Word, Image to PDF, PPT to PDF, compress PDF, merge PDF" />'
        # Insert after the existing keywords tag, or create one if it doesn't exist
        if '<meta name="keywords"' in base_html:
            base_html = base_html.replace('<meta name="keywords" content="file converter, PAPERPREP, PDF tools, PDF to Word, Image to PDF, PPT to PDF, compress PDF, merge PDF" />', keywords_meta)
        else:
            base_html = base_html.replace('</title>', f'</title>\n    {"PAPERPREP - Convert PDFs, Images & More"}')

    return base_html


@app.route('/')
def home():
    tools_html = """
    <h1>Welcome to PAPERPREP</h1>
    <h2>Your all-in-one document & image conversion tool</h2>
    <div class="tools-grid">
      <div class="tool-card" onclick="location.href='{}'" tabindex="0" role="button" aria-pressed="false">
        <i class="fas fa-file-pdf"></i>
        <h3>PDF to Word</h3>
      </div>
      <div class="tool-card" onclick="location.href='{}'" tabindex="0" role="button" aria-pressed="false">
        <i class="fas fa-file-image"></i>
        <h3>JPG to Word</h3>
      </div>
      <div class="tool-card" onclick="location.href='{}'" tabindex="0" role="button" aria-pressed="false">
        <i class="fas fa-file-powerpoint"></i>
        <h3>PPT to PDF</h3>
      </div>
      <div class="tool-card" onclick="location.href='{}'" tabindex="0" role="button" aria-pressed="false">
        <i class="fas fa-file-pdf"></i>
        <h3>PDF to PPT</h3>
      </div>
      <div class="tool-card" onclick="location.href='{}'" tabindex="0" role="button" aria-pressed="false">
        <i class="fas fa-file-image"></i>
        <h3>Multiple Images to PDF</h3>
      </div>
      <div class="tool-card" onclick="location.href='{}'" tabindex="0" role="button" aria-pressed="false">
        <i class="fas fa-file-pdf"></i>
        <h3>Merge PDF</h3>
      </div>
      <div class="tool-card" onclick="location.href='{}'" tabindex="0" role="button" aria-pressed="false">
        <i class="fas fa-compress"></i>
        <h3>Image Compressor</h3>
      </div>
      <div class="tool-card" onclick="location.href='{}'" tabindex="0" role="button" aria-pressed="false">
        <i class="fas fa-file-pdf"></i>
        <h3>PDF Compressor</h3>
      </div>
    </div>
    """.format(
        url_for('pdf_to_word'),
        url_for('jpg_to_word'),
        url_for('ppt_to_pdf'),
        url_for('pdf_to_ppt'),
        url_for('images_to_pdf'),
        url_for('merge_pdf'),
        url_for('image_compress'),
        url_for('pdf_compress'),
    )
    return render_page("Home", tools_html)


@app.route('/about')
def about():
    html = """
    <h1>About PAPERPREP</h1>
    <p>PAPERPREP is your ultimate college companion for document and image conversion and compression tools.</p>
    <p>This project was developed as a college assignment with a focus on usability, design, and functionality.</p>
    """
    return render_page("About", html)

@app.route('/privacy')
def privacy():
    html = """
    <h1>Privacy Policy</h1>
    <p>We respect your privacy. Any files you upload are processed temporarily and not stored or shared. No data is kept after processing.</p>
    """
    return render_page("Privacy", html)

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        message = request.form.get('message','').strip()
        if not name or not email or not message:
            flash("All fields are required.")
            return redirect(url_for('contact'))
        html = f"""
        <h1>Contact Us</h1>
        <p>Thank you for reaching out, {name}! We will get back to you shortly.</p>
        """
        return render_page("Contact", html)
    else:
        html = """
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
        """
        return render_page("Contact", html)

@app.route('/terms')
def terms():
    html = """
    <h1>Terms & Conditions</h1>
    <p>Use PAPERPREP responsibly. We do not guarantee 100% accuracy on conversions and are not liable for data loss.</p>
    <p>The software is provided as-is without warranties of any kind.</p>
    """
    return render_page("Terms & Conditions", html)


def render_form_page(title, heading, accept, multiple=False, note=None):
    multiple_attr = ' multiple' if multiple else ''
    note_html = f"<p><small>{note}</small></p>" if note else ""
    input_name = "file" if not multiple else "files"
    accept_attr = ','.join(accept)
    html = f"""
    <h1>{heading}</h1>
    <form method="post" enctype="multipart/form-data">
      <div class="form-group">
        <label for="{input_name}">Upload file{'s' if multiple else ''} ({accept_attr}):</label>
        <input type="file" id="{input_name}" name="{input_name}" accept="{accept_attr}"{multiple_attr} required />
      </div>
      <input type="submit" class="btn" value="Convert" />
    </form>
    {note_html}
    """
    return render_page(title, html)


@app.route('/pdf-to-word', methods=['GET','POST'])
def pdf_to_word():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename, 'pdf_to_word'):
            flash('Invalid file type')
            return redirect(request.url)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                pdf_path = os.path.join(tmpdir, secure_filename(file.filename))
                file.save(pdf_path)
                docx_path = os.path.join(tmpdir, 'converted.docx')
                cv = Converter(pdf_path)
                cv.convert(docx_path, start=0, end=None)
                cv.close()
                return send_file(docx_path, as_attachment=True, download_name='converted.docx')
        except Exception as e:
            flash(f'Conversion failed: {e}')
            return redirect(request.url)
    else:
        return render_form_page("PDF to Word", "PDF to Word Converter", ['.pdf'])


@app.route('/jpg-to-word', methods=['GET','POST'])
def jpg_to_word():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename, 'jpg_to_word'):
            flash('Invalid file type')
            return redirect(request.url)
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
                             as_attachment=True, download_name='converted.docx')
        except Exception as e:
            flash(f"OCR conversion failed: {e}")
            return redirect(request.url)
    else:
        return render_form_page("JPG to Word", "JPG to Word Converter (OCR)", ['.jpg','.jpeg','.png'])


@app.route('/ppt-to-pdf', methods=['GET','POST'])
def ppt_to_pdf():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename, 'ppt_to_pdf'):
            flash('Invalid file type')
            return redirect(request.url)
        # python-pptx cannot export slides as images easily, so we do a basic workaround
        # We'll just return a flash message that this feature is not fully implemented 
        flash("PPT to PDF conversion is not implemented fully as python-pptx can't save as PDF directly.")
        return redirect(request.url)
    else:
        return render_form_page("PPT to PDF", "PPT to PDF Converter", ['.pptx'])


@app.route('/pdf-to-ppt', methods=['GET','POST'])
def pdf_to_ppt():
    if convert_from_bytes is None:
        flash("PDF to PPT requires 'pdf2image' module. Please install it.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename, 'pdf_to_ppt'):
            flash('Invalid file type')
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
                    slide.shapes.add_picture(tmp_img_file.name, left, top, width=prs.slide_width, height=prs.slide_height)
            mem_file = io.BytesIO()
            prs.save(mem_file)
            mem_file.seek(0)
            return send_file(mem_file, mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                             as_attachment=True, download_name='converted.pptx')
        except Exception as e:
            flash(f"Conversion failed: {e}")
            return redirect(request.url)
    else:
        note = "Note: PDF pages will be converted as images into PPT slides."
        return render_form_page("PDF to PPT", "PDF to PPT Converter", ['.pdf'], note=note)


@app.route('/images-to-pdf', methods=['GET','POST'])
def images_to_pdf():
    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files or not any(f.filename for f in files):
            flash('No selected files')
            return redirect(request.url)
        images = []
        try:
            for file in files:
                if not allowed_file(file.filename, 'images_to_pdf'):
                    flash("Invalid file type in upload. Please upload images.")
                    return redirect(request.url)
                images.append(Image.open(file.stream).convert('RGB'))
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
    else:
        return render_form_page("Images to PDF", "Multiple Images to One PDF",
                                ['.jpg', '.jpeg', '.png', '.bmp', '.gif'], multiple=True)


@app.route('/merge-pdf', methods=['GET','POST'])
def merge_pdf():
    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files or not any(f.filename for f in files):
            flash('No selected files')
            return redirect(request.url)
        try:
            merger = PyPDF2.PdfMerger()
            for file in files:
                if not allowed_file(file.filename, 'merge_pdf'):
                    flash("Invalid file type in upload. Please upload PDFs.")
                    return redirect(request.url)
                file.stream.seek(0)
                merger.append(file.stream)
            mem_file = io.BytesIO()
            merger.write(mem_file)
            merger.close()
            mem_file.seek(0)
            return send_file(mem_file, mimetype='application/pdf', download_name='merged.pdf', as_attachment=True)
        except Exception as e:
            flash(f"Merging PDFs failed: {e}")
            return redirect(request.url)
    else:
        return render_form_page("Merge PDF", "Merge PDF Files", ['.pdf'], multiple=True)


@app.route('/image-compress', methods=['GET', 'POST'])
def image_compress():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename, 'image_compress'):
            flash('Invalid file type')
            return redirect(request.url)
        try:
            img = Image.open(file.stream).convert('RGB')
            mem_file = io.BytesIO()
            img.save(mem_file, format='JPEG', quality=40, optimize=True)
            mem_file.seek(0)
            return send_file(mem_file, mimetype='image/jpeg', download_name='compressed.jpg', as_attachment=True)
        except Exception as e:
            flash(f"Image compression failed: {e}")
            return redirect(request.url)
    else:
        return render_form_page("Image Compressor", "Image Compressor", ['.jpg', '.jpeg', '.png'])


@app.route('/pdf-compress', methods=['GET', 'POST'])
def pdf_compress():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename, 'pdf_compress'):
            flash('Invalid file type')
            return redirect(request.url)
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
        return render_form_page("PDF Compressor", "PDF Compressor", ['.pdf'])


if __name__ == '__main__':
    # Use 0.0.0.0 to be reachable on local network if hosting
    app.run(debug=True, host='0.0.0.0', port=5000)
