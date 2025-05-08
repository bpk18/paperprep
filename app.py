import os
import io
import tempfile
from flask import Flask, request, render_template_string, send_file, jsonify, url_for
from werkzeug.utils import secure_filename

from pdf2docx import Converter
from docx import Document
from docx.shared import Inches
from PIL import Image
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pptx import Presentation
from pdf2image import convert_from_path

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    'pdf', 'jpg', 'jpeg', 'png', 'ppt', 'pptx'
}

TOOLS = [
    {
        'name': 'PDF to Word',
        'icon': 'fas fa-file-pdf',
        'endpoint': 'pdf_to_word',
        'description': 'Convert PDF files into Word documents easily.',
        'accepted': ['pdf']
    },
    {
        'name': 'JPG to Word',
        'icon': 'fas fa-file-image',
        'endpoint': 'jpg_to_word',
        'description': 'Convert JPG images into Word documents.',
        'accepted': ['jpg', 'jpeg', 'png']
    },
    {
        'name': 'PPT to PDF',
        'icon': 'fas fa-file-powerpoint',
        'endpoint': 'ppt_to_pdf',
        'description': 'Convert PowerPoint presentations into PDF format quickly.',
        'accepted': ['ppt', 'pptx']
    },
    {
        'name': 'PDF to PPT',
        'icon': 'fas fa-file-pdf',
        'endpoint': 'pdf_to_ppt',
        'description': 'Transform PDF files into PowerPoint presentations.',
        'accepted': ['pdf']
    },
    {
        'name': 'Images to PDF',
        'icon': 'fas fa-file-image',
        'endpoint': 'images_to_pdf',
        'description': 'Combine multiple images into one PDF document.',
        'accepted': ['jpg', 'jpeg', 'png']
    },
    {
        'name': 'Merge PDF',
        'icon': 'fas fa-file-pdf',
        'endpoint': 'merge_pdf',
        'description': 'Merge multiple PDF files into one.',
        'accepted': ['pdf']
    },
    {
        'name': 'Image Compressor',
        'icon': 'fas fa-compress',
        'endpoint': 'image_compressor',
        'description': 'Compress images without losing quality.',
        'accepted': ['jpg', 'jpeg', 'png']
    },
    {
        'name': 'PDF Compressor',
        'icon': 'fas fa-compress',
        'endpoint': 'pdf_compressor',
        'description': 'Reduce PDF file sizes efficiently.',
        'accepted': ['pdf']
    }
]

# Removing About, Privacy, Contact, Terms from nav bar
NAV_ITEMS = []  # Empty nav for top bar

# Footer links for About, Privacy, Contact, Terms
FOOTER_LINKS = [
    {'name': 'About', 'endpoint': 'about'},
    {'name': 'Privacy', 'endpoint': 'privacy'},
    {'name': 'Contact', 'endpoint': 'contact'},
    {'name': 'Terms & Conditions', 'endpoint': 'terms'}
]

BASE_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>PAPERPREP - All in One File Converter </title>
<meta name="description" content="PAPERPREP is a fast, futuristic, and mobile-responsive document conversion tool. Easily convert PDF, Word, JPG, PPT, and more with smooth animations, dark/light mode toggle, and a sleek interface—perfect for students and professionals.">
<link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet"/>
<style>
  *, *::before, *::after {box-sizing: border-box;}
  body {
    margin: 0; padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
     Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
    background-color: #f4f8fb;
    color: #222;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    transition: background-color 0.3s ease, color 0.3s ease;
  }
  body.dark-theme {
    background-color: #121212;
    color: #e4e6eb;
  }
  nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background-color: #ffffffee;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
    backdrop-filter: saturate(180%) blur(10px);
  }
  body.dark-theme nav {
    background-color: #20232aee;
    box-shadow: 0 2px 8px rgba(255,255,255,0.1);
  }
  nav .brand {
    font-weight: 900;
    font-size: 1.8rem;
    color: #2962ff;
    cursor: default;
    display: flex;
    align-items: center;
  }
  nav .brand i {
    margin-right: 0.5rem;
  }
  nav ul {
    list-style: none;
    display: flex;
    gap: 1.2rem;
    margin: 0;
    padding: 0;
  }
  nav ul li a {
    color: inherit;
    font-weight: 600;
    font-size: 1rem;
    text-decoration: none;
    padding: 0.4rem 0.6rem;
    border-radius: 10px;
    transition: background-color 0.3s ease;
  }
  nav ul li a:hover {
    background-color: #2962ff;
    color: #fff;
  }
  #theme-toggle {
    border: 2px solid #2962ff;
    background: none;
    padding: 0.4rem 1rem;
    font-weight: 600;
    border-radius: 20px;
    cursor: pointer;
    color: #2962ff;
    transition: all 0.3s ease;
  }
  #theme-toggle:hover {
    background-color: #2962ff;
    color: white;
  }
  body.dark-theme #theme-toggle {
    border-color: #82b1ff;
    color: #82b1ff;
  }
  body.dark-theme #theme-toggle:hover {
    background-color: #82b1ff;
    color: #121212;
  }
  main.container {
    max-width: 1000px;
    margin: 2rem auto 4rem;
    padding: 0 1rem;
    flex-grow: 1;
    min-height: 600px;
  }
  h1.page-title {
    font-size: 2.8rem;
    margin-bottom: 1rem;
    font-weight: 900;
    color: #2962ff;
  }
  body.dark-theme h1.page-title {
    color: #82b1ff;
  }
  .tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill,minmax(180px,1fr));
    gap: 1.5rem;
  }
  @media(max-width: 768px) {
    .tools-grid {
      grid-template-columns: repeat(auto-fill,minmax(140px,1fr));
      gap:1rem;
    }
  }
  .tool-card {
    background: white;
    border-radius: 15px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    padding: 1.4rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    text-align: center;
    user-select: none;
    color: #222;
    text-decoration: none;
  }
  body.dark-theme .tool-card {
    background: #121212;
    color: #e4e6eb;
    box-shadow: 0 8px 16px rgba(255,255,255,0.1);
  }
  .tool-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    color: #2962ff;
  }
  body.dark-theme .tool-card:hover {
    color: #82b1ff;
  }
  .tool-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
  }
  form.upload-form {
    max-width: 400px;
    margin-top: 3rem;
    background: white;
    border-radius: 15px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    padding: 2rem 2.5rem;
  }
  body.dark-theme form.upload-form {
    background: #121212;
    box-shadow: 0 8px 24px rgba(255,255,255,0.1);
  }
  label {
    font-weight: 700;
    display: block;
    margin-bottom: 0.8rem;
  }
  input[type="file"] {
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    border: 2px solid #2962ff;
    font-size: 1rem;
    cursor: pointer;
    background: transparent;
    color: inherit;
    transition: border-color 0.3s ease;
  }
  input[type="file"]:hover,
  input[type="file"]:focus {
    border-color: #0039cb;
    outline: none;
  }
  button.submit-btn {
    margin-top: 1.6rem;
    width: 100%;
    padding: 14px 0;
    font-weight: 900;
    font-size: 1.3rem;
    border-radius: 30px;
    border: none;
    background-color: #2962ff;
    color: white;
    cursor: pointer;
    transition: background-color 0.3s ease;
    display:flex;
    justify-content:center;
    align-items:center;
  }
  button.submit-btn:hover,
  button.submit-btn:focus {
    background-color: #0039cb;
  }
  button.submit-btn.uploading {
    animation: pulse 1.8s infinite;
  }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(41, 98, 255, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(41, 98, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(41, 98, 255, 0); }
  }
  .flash-message {
    margin-top: 1.5rem;
    font-weight: 700;
    font-size: 1rem;
    padding: 1rem;
    border-radius: 15px;
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
    text-align: center;
    user-select: none;
  }
  body.dark-theme .flash-message {
    background-color: #223322;
    color: #a3d5a3;
    border-color: #3d6b3d;
  }
  footer {
    background: #f8fafa;
    border-top: 1px solid #ddd;
    padding: 1rem 1.5rem;
    text-align: center;
    font-size: 0.9rem;
    color: #555;
  }
  body.dark-theme footer {
    background: #1a1a1a;
    color: #bbb;
    border-top-color: #444;
  }
  footer a {
    color: #2962ff;
    margin: 0 0.6rem;
    text-decoration: none;
    font-weight: 600;
  }
  footer a:hover {
    text-decoration: underline;
  }
</style>
</head>
<body>
<nav>
  <div class="brand" aria-label="PAPERPREP Logo" tabindex="0"><i class="fas fa-file-alt"></i> PAPERPREP</div>
  <ul class="nav-links">
    {% for item in nav_items %}
        <li><a href="{{ url_for(item.endpoint) }}">{{ item.name }}</a></li>
    {% endfor %}
  </ul>
  <button id="theme-toggle" aria-label="Toggle Dark Theme">Dark Theme</button>
</nav>
<main class="container">
  {{ content | safe }}
</main>
<footer>
  <a href="{{ url_for('about') }}">About</a> |
  <a href="{{ url_for('privacy') }}">Privacy</a> |
  <a href="{{ url_for('contact') }}">Contact</a> |
  <a href="{{ url_for('terms') }}">Terms &amp; Conditions</a>
</footer>

<script>
  const themeToggleBtn = document.getElementById('theme-toggle');
  const body = document.body;

  if (localStorage.getItem('dark-theme') === 'true') {
    body.classList.add('dark-theme');
    themeToggleBtn.textContent = 'Light Theme';
  }

  themeToggleBtn.addEventListener('click', () => {
    const darkMode = body.classList.toggle('dark-theme');
    localStorage.setItem('dark-theme', darkMode);
    themeToggleBtn.textContent = darkMode ? 'Light Theme' : 'Dark Theme';
  });

  document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('.upload-form');
    forms.forEach(form => {
      form.addEventListener('submit', e => {
        e.preventDefault();
        const btn = form.querySelector('button[type=submit]');
        btn.disabled = true;
        btn.classList.add('uploading');
        btn.textContent = 'Uploading...';

        const formData = new FormData(form);

        let response;

        fetch(form.action, {
          method: 'POST',
          body: formData
        }).then(res => {
          response = res;
          if (!res.ok) throw new Error('Upload failed');
          return res.blob();
        }).then(blob => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          let disposition = response.headers.get('Content-Disposition');
          let filename = 'output';
          if (disposition && disposition.indexOf('filename=') !== -1) {
            const match = disposition.match(/filename="?([^"]+)"?/);
            if (match) filename = match[1];
          }
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          a.remove();
          window.URL.revokeObjectURL(url);
          btn.textContent = 'Success ✓';
          btn.classList.remove('uploading');
          btn.disabled = false;
          setTimeout(() => { btn.textContent = 'Upload'; }, 2000);
        }).catch(err => {
          alert('Error during upload: ' + err.message);
          btn.textContent = 'Upload';
          btn.classList.remove('uploading');
          btn.disabled = false;
        });
      });
    });
  });
</script>
</body>
</html>
'''

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def render_page(page_title, content):
    from flask import render_template_string
    return render_template_string(BASE_HTML, page_title=page_title, content=content,
                                  nav_items=NAV_ITEMS, footer_links=FOOTER_LINKS, url_for=url_for)

@app.route('/')
def home():
    items_html = '<h1 class="page-title">Welcome to PAPERPREP</h1>'
    items_html += '<p>Explore our powerful and fast file conversion and compression tools. Click on any tool to get started.</p>'
    items_html += '<div class="tools-grid">'
    for tool in TOOLS:
        items_html += f'''
          <a href="{url_for(tool['endpoint'])}" class="tool-card" aria-label="{tool['name']}">
              <i class="{tool['icon']} tool-icon"></i>
              <div class="tool-name">{tool['name']}</div>
              <div class="tool-desc">{tool['description']}</div>
          </a>
        '''
    items_html += '</div>'
    return render_page('Home', items_html)

def tool_page_html(tool, success_msg=None):
    accepted_ext_list = ", ".join(tool['accepted'])
    multiple = 'multiple' if tool['endpoint'] in ['images_to_pdf', 'merge_pdf'] else ''
    form_html = f'''
   <h1 class="page-title">{tool['name']}</h1>
   <p>{tool['description']}</p>
   <p><b>Accepted file types:</b> {accepted_ext_list}</p>
   <form class="upload-form" method="POST" enctype="multipart/form-data" aria-label="Upload file form" action="{url_for(tool['endpoint'])}">
     <label for="file" style="font-weight:600; margin-bottom:0.5rem; display:block;">Choose file{'s' if multiple else ''}</label>
     <input class="file-input" type="file" name="file" id="file" accept="{','.join(['.'+e for e in tool['accepted']])}" {multiple} required aria-required="true"/>
     <button type="submit" class="submit-btn">Upload</button>
   </form>
   '''
    if success_msg:
        form_html += f'<div class="flash-message" role="alert">{success_msg}</div>'
    return render_page(tool['name'], form_html)

def pdf_to_word_convert(input_path, output_path):
    converter = Converter(input_path)
    converter.convert(output_path, start=0, end=None)
    converter.close()

def jpg_to_word_convert(input_path, output_path):
    doc = Document()
    doc.add_picture(input_path, width=Inches(6))
    doc.save(output_path)

def ppt_to_pdf_convert(input_path, output_path):
    prs = Presentation(input_path)
    temp_dir = tempfile.mkdtemp()
    images = []
    try:
        for i, slide in enumerate(prs.slides):
            img_path = os.path.join(temp_dir, f"slide_{i+1}.png")
            slide_width = prs.slide_width
            slide_height = prs.slide_height
            # Create a white image placeholder for slide
            blank_img = Image.new("RGB", (int(slide_width / 9525), int(slide_height / 9525)), "white")
            blank_img.save(img_path)
            images.append(img_path)
        images_to_pdf_convert(images, output_path)
    finally:
        for img_file in images:
            os.remove(img_file)
        os.rmdir(temp_dir)

def pdf_to_ppt_convert(input_path, output_path):
    presentation = Presentation()
    slides = convert_from_path(input_path)
    for slide_img in slides:
        slide = presentation.slides.add_slide(presentation.slide_layouts[6])
        image_stream = io.BytesIO()
        slide_img.save(image_stream, format='PNG')
        image_stream.seek(0)
        slide.shapes.add_picture(image_stream, 0, 0, width=presentation.slide_width, height=presentation.slide_height)
    presentation.save(output_path)

def images_to_pdf_convert(input_paths, output_path):
    images = []
    for file_path in input_paths:
        im = Image.open(file_path)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        images.append(im)
    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:])

def merge_pdfs(input_paths, output_path):
    merger = PdfMerger()
    for pdf in input_paths:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()

def image_compress(input_path, output_path):
    im = Image.open(input_path)
    im.save(output_path, optimize=True, quality=30)

def pdf_compress(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(output_path, 'wb') as f_out:
        writer.write(f_out)

def save_upload(file_storage):
    filename = secure_filename(file_storage.filename)
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, filename)
    file_storage.save(file_path)
    return file_path, temp_dir, filename

import shutil

def make_route(tool):
    def tool_func():
        if request.method == 'POST':
            files = request.files.getlist('file')
            if not files or all(f.filename == '' for f in files):
                return jsonify({'error': 'No file selected'}), 400
            for f in files:
                if not allowed_file(f.filename, tool['accepted']):
                    return jsonify({'error': f'Unsupported file type: {f.filename}'}), 400
            temp_dirs = []
            input_paths = []
            try:
                for f in files:
                    p, d, fname = save_upload(f)
                    input_paths.append(p)
                    temp_dirs.append(d)
                out_filename = "output"
                if tool['endpoint'] == 'pdf_to_word':
                    out_filename += ".docx"
                elif tool['endpoint'] == 'jpg_to_word':
                    out_filename += ".docx"
                elif tool['endpoint'] == 'ppt_to_pdf':
                    out_filename += ".pdf"
                elif tool['endpoint'] == 'pdf_to_ppt':
                    out_filename += ".pptx"
                elif tool['endpoint'] == 'images_to_pdf':
                    out_filename += ".pdf"
                elif tool['endpoint'] == 'merge_pdf':
                    out_filename += ".pdf"
                elif tool['endpoint'] == 'image_compressor':
                    ext = os.path.splitext(input_paths[0])[1].lower()
                    out_filename += ext
                elif tool['endpoint'] == 'pdf_compressor':
                    out_filename += ".pdf"
                else:
                    out_filename += ".out"
                out_path = os.path.join(tempfile.mkdtemp(), out_filename)
                if tool['endpoint'] == 'pdf_to_word':
                    pdf_to_word_convert(input_paths[0], out_path)
                elif tool['endpoint'] == 'jpg_to_word':
                    jpg_to_word_convert(input_paths[0], out_path)
                elif tool['endpoint'] == 'ppt_to_pdf':
                    ppt_to_pdf_convert(input_paths[0], out_path)
                elif tool['endpoint'] == 'pdf_to_ppt':
                    pdf_to_ppt_convert(input_paths[0], out_path)
                elif tool['endpoint'] == 'images_to_pdf':
                    images_to_pdf_convert(input_paths, out_path)
                elif tool['endpoint'] == 'merge_pdf':
                    merge_pdfs(input_paths, out_path)
                elif tool['endpoint'] == 'image_compressor':
                    image_compress(input_paths[0], out_path)
                elif tool['endpoint'] == 'pdf_compressor':
                    pdf_compress(input_paths[0], out_path)
                else:
                    return jsonify({'error': 'Conversion not implemented.'}), 400
                return send_file(out_path, as_attachment=True, download_name=out_filename)
            finally:
                for d in temp_dirs:
                    shutil.rmtree(d, ignore_errors=True)
        return tool_page_html(tool)
    tool_func.__name__ = tool['endpoint']
    return tool_func

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

for tool in TOOLS:
    app.add_url_rule(f'/{tool["endpoint"]}', view_func=make_route(tool), methods=['GET', 'POST'])

def static_page_html(title, content):
    return f'''
    <h1 class="page-title">{title}</h1>
    <div style="max-width:700px; white-space: pre-line;">
    {content}
    </div>
    '''

@app.route('/about')
def about():
    content = (
        "PAPERPREP is a fast, efficient, and futuristic file conversion web application designed "
        "for all your document needs. Built with cutting-edge technology and a sleek UI for an "
        "awesome user experience."
    )
    return render_page('About', static_page_html('About', content))

@app.route('/privacy')
def privacy():
    content = (
        "Your privacy is important to us. We do not store your uploaded files or share any data. "
        "All processing is done securely and temporarily."
    )
    return render_page('Privacy Policy', static_page_html('Privacy Policy', content))

@app.route('/contact')
def contact():
    content = (
        "Contact us at:\n\n"
        "Email: support@paperprep.com\n"
        "Phone: +1 234 567 8900\n"
        "Address: 123 College St, City, Country"
    )
    return render_page('Contact', static_page_html('Contact', content))

@app.route('/terms')
def terms():
    content = (
        "Terms and Conditions:\n\n"
        "Use PAPERPREP at your own risk. We strive to provide accurate conversions but "
        "do not guarantee results. By using the service, you accept our terms."
    )
    return render_page('Terms and Conditions', static_page_html('Terms and Conditions', content))

def render_page(page_title, content):
    from flask import render_template_string
    return render_template_string(BASE_HTML, page_title=page_title, content=content,
                                  nav_items=NAV_ITEMS, footer_links=FOOTER_LINKS, url_for=url_for)


@app.route('/seo-tags')

def seo_tags():

    # Render the seo.html template with SEO meta tags

    return render_template_string(open('templates/seo.html').read())

if __name__ == '__main__':
    app.run(host='8.8.8.8', port=8000, debug=True)
