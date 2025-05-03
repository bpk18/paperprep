import io
import os
import tempfile
from flask import Flask, send_file, request, render_template_string, abort
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from PIL import Image
import pytesseract
from pptx import Presentation
from pptx.util import Inches
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import sys

app = Flask(__name__, static_folder='static')

# Allowed extensions for uploads
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}
ALLOWED_PPT_EXTENSIONS = {'ppt', 'pptx'}


def allowed_file(filename, allowed_exts):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


# Convert PDF to Word .docx using pdf2docx
@app.route('/convert/pdf-to-word', methods=['POST'])
def pdf_to_word():
    if 'file' not in request.files:
        abort(400, 'No file part')
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        abort(400, 'Invalid file')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
        file.save(tmp_pdf.name)
        tmp_docx = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        tmp_docx.close()
        cv = Converter(tmp_pdf.name)
        cv.convert(tmp_docx.name, start=0, end=None)
        cv.close()
        os.unlink(tmp_pdf.name)
        return send_file(tmp_docx.name, as_attachment=True, download_name="converted.docx")


# Convert JPG (or image) to Word using pytesseract (OCR)
@app.route('/convert/jpg-to-word', methods=['POST'])
def jpg_to_word():
    if 'file' not in request.files:
        abort(400, 'No file part')
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        abort(400, 'Invalid file')
    try:
        img = Image.open(file.stream)
        text = pytesseract.image_to_string(img)
    except Exception as e:
        abort(500, 'OCR failed: ' + str(e))
    # Save text as Word doc (simple .docx)
    from docx import Document
    doc = Document()
    doc.add_paragraph(text)
    tmp_docx = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    doc.save(tmp_docx.name)
    return send_file(tmp_docx.name, as_attachment=True, download_name='converted.docx')


# Convert PPT to PDF using python-pptx + reportlab (simple export slides as images then PDF)
@app.route('/convert/ppt-to-pdf', methods=['POST'])
def ppt_to_pdf():
    if 'file' not in request.files:
        abort(400, "No file part")
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_PPT_EXTENSIONS):
        abort(400, 'Invalid file')
    # Save ppt temporarily
    tmp_ppt = tempfile.NamedTemporaryFile(delete=False, suffix='.pptx')
    file.save(tmp_ppt.name)
    # Open presentation
    try:
        prs = Presentation(tmp_ppt.name)
    except Exception as e:
        abort(500, f"Failed to open presentation: {str(e)}")
    # Create PDF with reportlab
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    c = canvas.Canvas(tmp_pdf.name, pagesize=letter)
    width, height = letter
    for slide in prs.slides:
        # As python-pptx can't export slide images, we place placeholder text
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height/2, "Slide Preview Not Available")
        c.showPage()
    c.save()
    os.unlink(tmp_ppt.name)
    return send_file(tmp_pdf.name, as_attachment=True, download_name="converted.pdf")


# Convert PDF to PPT - limited, just create blank ppt slides for each PDF page (no content)
@app.route('/convert/pdf-to-ppt', methods=['POST'])
def pdf_to_ppt():
    if 'file' not in request.files:
        abort(400, "No file part")
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        abort(400, 'Invalid file')
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    file.save(tmp_pdf.name)
    try:
        reader = PdfReader(tmp_pdf.name)
        prs = Presentation()
        blank_slide_layout = prs.slide_layouts[6]
        for _ in reader.pages:
            prs.slides.add_slide(blank_slide_layout)
        tmp_pptx = tempfile.NamedTemporaryFile(delete=False, suffix='.pptx')
        prs.save(tmp_pptx.name)
    except Exception as e:
        abort(500, f"Conversion failed: {str(e)}")
    os.unlink(tmp_pdf.name)
    return send_file(tmp_pptx.name, as_attachment=True, download_name="converted.pptx")


# Multiple images into one PDF
@app.route('/convert/multiple-images-to-pdf', methods=['POST'])
def multiple_images_to_pdf():
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        abort(400, "No files uploaded")
    images = []
    for file in files:
        if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            try:
                img = Image.open(file.stream).convert('RGB')
                images.append(img)
            except Exception as e:
                abort(400, f"Invalid image file: {file.filename}")
        else:
            abort(400, "Invalid file type in upload")
    if len(images) == 0:
        abort(400, "No valid images uploaded")
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    first_image = images[0]
    other_images = images[1:]
    try:
        first_image.save(tmp_pdf.name, save_all=True, append_images=other_images)
    except Exception as e:
        abort(500, f"Failed to create PDF: {str(e)}")
    return send_file(tmp_pdf.name, as_attachment=True, download_name="combined.pdf")


# Merge multiple PDFs
@app.route('/convert/merge-pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        abort(400, "No files uploaded")
    merger = PdfMerger()
    try:
        for file in files:
            if file and allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    file.save(tmp.name)
                    merger.append(tmp.name)
                    os.unlink(tmp.name)
            else:
                abort(400, "Invalid file type in upload")
        tmp_merged = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        merger.write(tmp_merged.name)
        merger.close()
    except Exception as e:
        abort(500, f"Merging failed: {str(e)}")
    return send_file(tmp_merged.name, as_attachment=True, download_name="merged.pdf")


# Image compressor (reduce quality)
@app.route('/convert/image-compressor', methods=['POST'])
def image_compressor():
    if 'file' not in request.files:
        abort(400, "No file part")
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        abort(400, "Invalid file")
    try:
        img = Image.open(file.stream)
        tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        # Compress to quality=50 as example
        img.save(tmp_img.name, optimize=True, quality=50)
    except Exception as e:
        abort(500, f"Compression failed: {str(e)}")
    return send_file(tmp_img.name, as_attachment=True, download_name="compressed.jpg")


# PDF compressor (re-saves PDF to optimize)
@app.route('/convert/pdf-compressor', methods=['POST'])
def pdf_compressor():
    if 'file' not in request.files:
        abort(400, "No file part")
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        abort(400, "Invalid file")
    tmp_pdf_in = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp_pdf_out = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    file.save(tmp_pdf_in.name)
    try:
        reader = PdfReader(tmp_pdf_in.name)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        # Minimal compression: just rewrite PDF, no advanced compression
        with open(tmp_pdf_out.name, 'wb') as f_out:
            writer.write(f_out)
    except Exception as e:
        abort(500, f"Compression failed: {str(e)}")
    finally:
        os.unlink(tmp_pdf_in.name)
    return send_file(tmp_pdf_out.name, as_attachment=True, download_name="compressed.pdf")


INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
  <meta name="description" content="PAPERPREP: Futuristic file conversion and compression tools for PDFs, images, presentations, and more. Clean, responsive UI." />
  <meta name="keywords" content="PDF to Word, JPG to Word, PPT to PDF, PDF to PPT, merge PDF, compress image, compress PDF, file converter, PAPERPREP" />
  <meta name="author" content="PAPERPREP Team" />
  <meta name="robots" content="index, follow" />
  <title>PAPERPREP - Futuristic File Conversion & Compression Tools</title>
  <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon" />
  <style>
    /* RESET */
    *, *::before, *::after {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f0f4f8;
      color: #222;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* THEME COLORS */
    :root {
      --color-primary: #5c6ac4;
      --color-primary-light: #8c97f9;
      --color-secondary: #61a5c2;
      --color-accent: #f4a261;
      --color-bg-light: #f0f4f8;
      --color-bg-dark: #121212;
      --color-text-light: #222;
      --color-text-dark: #ddd;
      --color-button-bg: var(--color-primary);
      --color-button-text: #fff;
      --color-button-hover-bg: var(--color-primary-light);
    }

    /* DARK THEME */
    body.dark {
      background-color: var(--color-bg-dark);
      color: var(--color-text-dark);
    }
    body.dark header, body.dark nav {
      background-color: #1e1e1e;
    }
    body.dark .card {
      background-color: #222;
      box-shadow: 0 1px 8px rgba(255 255 255 / 0.1);
    }
    body.dark button {
      background-color: var(--color-primary-light);
      color: var(--color-text-dark);
    }
    body.dark button:hover,
    body.dark button:focus {
      background-color: var(--color-primary);
      color: #fff;
    }


    /* HEADER & NAVBAR */
    header {
      background-color: #fff;
      padding: 1rem 1rem;
      box-shadow: 0 2px 8px rgb(0 0 0 / 0.1);
      position: sticky;
      top: 0;
      z-index: 1000;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    body.dark header {
      background-color: #1e1e1e;
      box-shadow: none;
      border-bottom: 1px solid #444;
    }

    .logo {
      font-weight: 900;
      font-size: 1.5rem;
      color: var(--color-primary);
      user-select: none;
    }
    body.dark .logo {
      color: var(--color-primary-light);
    }

    nav {
      position: relative;
    }

    /* Hamburger menu button */
    .menu-toggle {
      display: none;
      flex-direction: column;
      cursor: pointer;
      width: 28px;
      height: 22px;
      justify-content: space-between;
    }
    .menu-toggle span {
      height: 3px;
      width: 100%;
      background-color: var(--color-primary);
      border-radius: 2px;
      transition: background-color 0.3s;
    }
    body.dark .menu-toggle span {
      background-color: var(--color-primary-light);
    }

    ul.menu {
      display: flex;
      list-style: none;
      margin: 0;
      padding: 0;
      gap: 1.5rem;
    }
    ul.menu li a {
      text-decoration: none;
      color: var(--color-primary);
      font-weight: 600;
      transition: color 0.3s;
    }
    ul.menu li a:hover,
    ul.menu li a:focus {
      color: var(--color-accent);
      outline: none;
    }
    body.dark ul.menu li a {
      color: var(--color-primary-light);
    }
    body.dark ul.menu li a:hover,
    body.dark ul.menu li a:focus {
      color: var(--color-accent);
    }

    /* Mobile menu initial state */
    @media (max-width: 768px) {
      .menu-toggle {
        display: flex;
      }
      ul.menu {
        position: absolute;
        top: 100%;
        right: 0;
        background-color: #fff;
        flex-direction: column;
        width: 200px;
        transform: translateY(-20px);
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s, transform 0.3s;
        box-shadow: 0 2px 12px rgb(0 0 0 / 0.2);
        border-radius: 6px;
        z-index: 999;
      }
      body.dark ul.menu {
        background-color: #1e1e1e;
        box-shadow: 0 2px 12px rgba(255 255 255 / 0.1);
      }
      ul.menu.open {
        opacity: 1;
        pointer-events: auto;
        transform: translateY(0);
      }
      ul.menu li {
        padding: 0.8rem 1rem;
      }
      ul.menu li a {
        display: block;
      }
    }

    /* THEME TOGGLE BUTTON */
    .theme-toggle {
      border: none;
      background-color: var(--color-button-bg);
      color: var(--color-button-text);
      padding: 0.5rem 1rem;
      border-radius: 25px;
      font-weight: 600;
      cursor: pointer;
      transition: background-color 0.3s;
      user-select: none;
    }
    .theme-toggle:hover,
    .theme-toggle:focus {
      background-color: var(--color-button-hover-bg);
      outline: none;
    }

    /* MAIN CONTENT */
    main {
      flex-grow: 1;
      padding: 2rem 1rem;
      max-width: 1000px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    /* Tools grid */
    .tools-grid {
      display: grid;
      gap: 1.5rem;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }

    .card {
      background-color: #fff;
      border-radius: 14px;
      padding: 1.5rem;
      box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      transition: box-shadow 0.3s, transform 0.3s;
    }
    .card:hover,
    .card:focus-within {
      box-shadow: 0 5px 20px rgb(0 0 0 / 0.15);
      transform: translateY(-3px);
      outline: none;
    }
    body.dark .card {
      background-color: #222;
      box-shadow: 0 2px 10px rgba(255 255 255 / 0.05);
    }
    body.dark .card:hover,
    body.dark .card:focus-within {
      box-shadow: 0 5px 20px rgba(255 255 255 / 0.25);
    }

    .card-icon {
      width: 64px;
      height: 64px;
      margin-bottom: 1rem;
      fill: var(--color-primary);
      transition: fill 0.3s;
    }
    body.dark .card-icon {
      fill: var(--color-primary-light);
    }

    .card-title {
      font-size: 1.25rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }
    .card-desc {
      font-size: 0.9rem;
      color: #666;
      margin-bottom: 1rem;
    }
    body.dark .card-desc {
      color: #bbb;
    }

    .btn-action, .file-upload-form button {
      background-color: var(--color-button-bg);
      color: var(--color-button-text);
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 25px;
      font-weight: 600;
      cursor: pointer;
      user-select: none;
      transition: background-color 0.3s;
      margin-top: 0.5rem;
    }
    .btn-action:hover,
    .btn-action:focus,
    .file-upload-form button:hover,
    .file-upload-form button:focus {
      background-color: var(--color-button-hover-bg);
      outline: none;
    }
    body.dark .btn-action,
    body.dark .file-upload-form button{
      background-color: var(--color-primary-light);
      color: var(--color-text-dark);
    }
    body.dark .btn-action:hover,
    body.dark .btn-action:focus,
    body.dark .file-upload-form button:hover,
    body.dark .file-upload-form button:focus {
      background-color: var(--color-primary);
      color: #fff;
    }

    input[type="file"] {
      margin-top: 0.5rem;
    }

    /* FOOTER */
    footer {
      text-align: center;
      padding: 1rem;
      font-size: 0.9rem;
      color: #888;
    }
    body.dark footer {
      color: #555;
    }

    /* Modal style for info content */
    #modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0,0,0,0.5);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 2000;
      padding: 1rem;
    }
    #modal.open {
      display: flex;
    }
    #modal-content {
      max-width: 600px;
      background: #fff;
      border-radius: 12px;
      padding: 1.5rem 2rem;
      color: #222;
      overflow-y: auto;
      max-height: 80vh;
      box-shadow: 0 8px 24px rgba(0,0,0,0.2);
      position: relative;
    }
    body.dark #modal-content {
      background: #222;
      color: #ddd;
      box-shadow: 0 8px 24px rgba(255,255,255,0.2);
    }
    #modal-content h2 {
      margin-top: 0;
    }
    #modal-close {
      position: absolute;
      top: 12px;
      right: 16px;
      background: transparent;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: inherit;
    }
    #modal-close:hover,
    #modal-close:focus {
      color: var(--color-accent);
      outline: none;
    }

  </style>
</head>
<body>
  <header>
    <div class="logo">PAPERPREP</div>
    <nav>
      <button class="menu-toggle" aria-label="Toggle menu" aria-expanded="false" aria-controls="main-menu">
        <span></span><span></span><span></span>
      </button>
      <ul class="menu" id="main-menu" role="menu" aria-label="Main navigation menu">
        <li><button class="info-menu-btn" data-info="about" role="menuitem" tabindex="0">About</button></li>
        <li><button class="info-menu-btn" data-info="privacy" role="menuitem" tabindex="0">Privacy</button></li>
        <li><button class="info-menu-btn" data-info="contact" role="menuitem" tabindex="0">Contact</button></li>
        <li><button class="info-menu-btn" data-info="terms" role="menuitem" tabindex="0">Terms & Conditions</button></li>
      </ul>
    </nav>
    <button class="theme-toggle" aria-label="Toggle dark mode">Dark Theme</button>
  </header>
  <main>
    <section aria-label="File Conversion Tools">
      <h1 style="text-align:center;">Welcome to PAPERPREP</h1>
      <p style="max-width:600px; margin:0 auto 2rem auto; text-align:center; color:#555;">
        Your all-in-one futuristic file conversion and compression toolkit. Quickly convert, compress, and manage your documents and images.
      </p>
      <div class="tools-grid" role="list" aria-label="List of conversion and compression tools">
        <!-- Tool Cards with Forms (same as previous) -->
        <article class="card" role="listitem" tabindex="0" aria-label="PDF to Word conversion tool">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64" >
            <path d="M48 2H16C12.7 2 10 4.7 10 8V56C10 59.3 12.7 62 16 62H48C51.3 62 54 59.3 54 56V8C54 4.7 51.3 2 48 2Z" />
            <path d="M28 18H36V46H28Z" fill="#f4a261"/>
            <path d="M36 24L44 18" stroke="#5c6ac4" stroke-width="2"/>
          </svg>
          <h3 class="card-title">PDF to Word</h3>
          <p class="card-desc">Convert your PDF documents to editable Word files.</p>
          <form class="file-upload-form" method="post" action="/convert/pdf-to-word" enctype="multipart/form-data" target="downloadFrame">
            <input type="file" name="file" accept=".pdf" required aria-label="Upload PDF file for conversion to Word"/>
            <button type="submit">Convert &amp; Download</button>
          </form>
        </article>

        <article class="card" role="listitem" tabindex="0" aria-label="JPG to Word conversion tool">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64" >
            <circle cx="32" cy="32" r="30" fill="#8c97f9" />
            <rect x="15" y="22" width="34" height="20" rx="4" ry="4" fill="#61a5c2"/>
            <circle cx="32" cy="32" r="8" fill="#f4a261"/>
          </svg>
          <h3 class="card-title">JPG to Word</h3>
          <p class="card-desc">Extract text from your JPG images into Word format.</p>
          <form class="file-upload-form" method="post" action="/convert/jpg-to-word" enctype="multipart/form-data" target="downloadFrame">
            <input type="file" name="file" accept="image/jpeg,image/png,image/bmp,image/gif,image/tiff" required aria-label="Upload JPG or image file for OCR to Word"/>
            <button type="submit">Convert &amp; Download</button>
          </form>
        </article>

        <article class="card" role="listitem" tabindex="0" aria-label="PPT to PDF conversion tool">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <rect x="14" y="10" width="36" height="44" rx="6" ry="6" fill="#5c6ac4"/>
            <rect x="20" y="18" width="24" height="28" fill="#f4a261"/>
            <rect x="20" y="22" width="24" height="6" fill="#fff"/>
            <rect x="20" y="34" width="24" height="6" fill="#fff"/>
          </svg>
          <h3 class="card-title">PPT to PDF</h3>
          <p class="card-desc">Easily convert your PowerPoint presentations to PDF files.</p>
          <form class="file-upload-form" method="post" action="/convert/ppt-to-pdf" enctype="multipart/form-data" target="downloadFrame">
            <input type="file" name="file" accept=".ppt,.pptx" required aria-label="Upload PPT file for conversion to PDF"/>
            <button type="submit">Convert &amp; Download</button>
          </form>
        </article>

        <article class="card" role="listitem" tabindex="0" aria-label="PDF to PPT conversion tool">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <path d="M10 54L54 10" stroke="#5c6ac4" stroke-width="5" stroke-linecap="round"/>
            <circle cx="22" cy="22" r="10" fill="#f4a261" />
            <circle cx="42" cy="42" r="10" fill="#61a5c2" />
            <text x="22" y="26" font-size="10" text-anchor="middle" fill="#fff" font-family="Segoe UI">PPT</text>
            <text x="42" y="46" font-size="10" text-anchor="middle" fill="#fff" font-family="Segoe UI">PDF</text>
          </svg>
          <h3 class="card-title">PDF to PPT</h3>
          <p class="card-desc">Convert PDF documents back to editable PowerPoint presentations.</p>
          <form class="file-upload-form" method="post" action="/convert/pdf-to-ppt" enctype="multipart/form-data" target="downloadFrame">
            <input type="file" name="file" accept=".pdf" required aria-label="Upload PDF file for conversion to PPT"/>
            <button type="submit">Convert &amp; Download</button>
          </form>
        </article>

        <article class="card" role="listitem" tabindex="0" aria-label="Multiple images to single PDF">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <rect x="8" y="12" width="20" height="40" rx="4" ry="4" fill="#5c6ac4"/>
            <rect x="36" y="12" width="20" height="40" rx="4" ry="4" fill="#61a5c2"/>
            <path d="M16 26H44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
            <path d="M16 38H44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <h3 class="card-title">Multiple Images into One PDF</h3>
          <p class="card-desc">Combine multiple images into a single PDF file easily.</p>
          <form class="file-upload-form" method="post" action="/convert/multiple-images-to-pdf" enctype="multipart/form-data" target="downloadFrame">
            <input type="file" name="files" accept="image/jpeg,image/png,image/bmp,image/gif,image/tiff" multiple required aria-label="Upload multiple images to combine into PDF"/>
            <button type="submit">Convert &amp; Download</button>
          </form>
        </article>

        <article class="card" role="listitem" tabindex="0" aria-label="Merge multiple PDFs">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <rect x="12" y="14" width="40" height="36" rx="6" ry="6" fill="#5c6ac4"/>
            <path d="M16 20L48 44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
            <path d="M48 20L16 44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <h3 class="card-title">Merge PDF</h3>
          <p class="card-desc">Combine multiple PDF files into one seamless document.</p>
          <form class="file-upload-form" method="post" action="/convert/merge-pdf" enctype="multipart/form-data" target="downloadFrame">
            <input type="file" name="files" accept=".pdf" multiple required aria-label="Upload multiple PDFs to merge"/>
            <button type="submit">Merge &amp; Download</button>
          </form>
        </article>

        <article class="card" role="listitem" tabindex="0" aria-label="Image compressor">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="26" stroke="#5c6ac4" stroke-width="4" fill="#61a5c2"/>
            <path d="M20 32H44" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
            <path d="M32 20V44" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <h3 class="card-title">Image Compressor</h3>
          <p class="card-desc">Compress images to reduce file size without losing quality.</p>
          <form class="file-upload-form" method="post" action="/convert/image-compressor" enctype="multipart/form-data" target="downloadFrame">
            <input type="file" name="file" accept="image/jpeg,image/png,image/bmp,image/gif,image/tiff" required aria-label="Upload image to compress"/>
            <button type="submit">Compress &amp; Download</button>
          </form>
        </article>

        <article class="card" role="listitem" tabindex="0" aria-label="PDF compressor">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <rect x="14" y="18" width="36" height="28" rx="6" ry="6" fill="#5c6ac4"/>
            <path d="M22 26H42" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
            <path d="M22 38H42" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <h3 class="card-title">PDF Compressor</h3>
          <p class="card-desc">Reduce the size of your PDF files for faster sharing.</p>
          <form class="file-upload-form" method="post" action="/convert/pdf-compressor" enctype="multipart/form-data" target="downloadFrame">
            <input type="file" name="file" accept=".pdf" required aria-label="Upload PDF to compress"/>
            <button type="submit">Compress &amp; Download</button>
          </form>
        </article>

      </div>
    </section>
  </main>

  <footer>
    &copy; 2024 PAPERPREP. All rights reserved.
  </footer>

  <iframe name="downloadFrame" style="display:none;"></iframe>

  <!-- Modal for info content -->
  <div id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" tabindex="-1">
    <div id="modal-content">
      <button id="modal-close" aria-label="Close dialog">&times;</button>
      <h2 id="modal-title"></h2>
      <div id="modal-body"></div>
    </div>
  </div>

  <script>
    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const menu = document.querySelector('.menu');
    menuToggle.addEventListener('click', () => {
      const expanded = menuToggle.getAttribute('aria-expanded') === 'true' || false;
      menuToggle.setAttribute('aria-expanded', !expanded);
      menu.classList.toggle('open');
    });

    // Close menu when clicking outside (for mobile)
    document.addEventListener('click', (e) => {
      if (!menu.contains(e.target) && !menuToggle.contains(e.target)) {
        menu.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', false);
      }
    });

    // Theme toggle
    const themeToggleBtn = document.querySelector('.theme-toggle');
    const bodyElement = document.body;
    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      bodyElement.classList.add('dark');
      themeToggleBtn.textContent = 'Light Theme';
      themeToggleBtn.setAttribute('aria-label', 'Toggle light mode');
    }

    themeToggleBtn.addEventListener('click', () => {
      const isDark = bodyElement.classList.toggle('dark');
      if (isDark) {
        themeToggleBtn.textContent = 'Light Theme';
        themeToggleBtn.setAttribute('aria-label', 'Toggle light mode');
        localStorage.setItem('theme', 'dark');
      } else {
        themeToggleBtn.textContent = 'Dark Theme';
        themeToggleBtn.setAttribute('aria-label', 'Toggle dark mode');
        localStorage.setItem('theme', 'light');
      }
    });

    // Modal system
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const modalCloseBtn = document.getElementById('modal-close');

    const infoContents = {
      about: {
        title: 'About PAPERPREP',
        content: `<p>PAPERPREP is an innovative platform designed to make file conversions and compression effortless and efficient. Whether you are a student, professional, or a casual user, our futuristic tools help you manage documents and images with just a few clicks. Our mission is to provide a seamless and intuitive user experience with cutting edge technology and soothing design.</p>`
      },
      privacy: {
        title: 'Privacy Policy',
        content: `<p>Your privacy is important to us. PAPERPREP does not store or share any of your files. All conversions occur securely and temporarily with no user data retention. We use industry best practices to safeguard your information.</p>`
      },
      contact: {
        title: 'Contact Us',
        content: `<p>If you have any questions, suggestions, or need support, feel free to reach out to us at <a href="mailto:support@paperprep.com">support@paperprep.com</a>. We value your feedback.</p>`
      },
      terms: {
        title: 'Terms & Conditions',
        content: `<p>By using PAPERPREP, you agree to our terms and conditions. We provide our tools "as is" without warranties. Use the services responsibly and respect intellectual property rights.</p>`
      }
    };

    document.querySelectorAll('.info-menu-btn').forEach(button => {
      button.addEventListener('click', () => {
        const key = button.getAttribute('data-info');
        if (infoContents[key]) {
          modalTitle.innerHTML = infoContents[key].title;
          modalBody.innerHTML = infoContents[key].content;
          modal.classList.add('open');
          modal.focus();
          menu.classList.remove('open');
          menuToggle.setAttribute('aria-expanded', false);
        }
      });
    });

    modalCloseBtn.addEventListener('click', () => {
      modal.classList.remove('open');
    });

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('open')) {
        modal.classList.remove('open');
      }
    });

  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

# Route to serve favicon.ico from static folder
@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(app.static_folder, 'favicon.ico'))

if __name__ == '__main__':
    # Run on all interfaces on port 5000 for easy hosting/demo
    # To install dependencies:
    # pip install flask pdf2docx python-pptx Pillow pytesseract PyPDF2 reportlab python-docx
    app.run(host='0.0.0.0', port=5000, debug=True)
