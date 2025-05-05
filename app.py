import os
import io
import tempfile
from flask import Flask, request, redirect, url_for, flash, render_template_string, send_file, jsonify
from werkzeug.utils import secure_filename

import pytesseract
from pdf2docx import Converter
from docx import Document
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
        'description': 'Convert JPG images into editable Word documents.',
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
    },
]

NAV_ITEMS = [
    {'name': 'About', 'endpoint': 'about'},
    {'name': 'Privacy', 'endpoint': 'privacy'},
    {'name': 'Contact', 'endpoint': 'contact'},
    {'name': 'Terms & Conditions', 'endpoint': 'terms'},
]

BASE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PAPERPREP - {{ page_title }}</title>
  <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet"/>
  <style>
    body {
      margin: 0; padding:0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f0f4f8;
      color: #222;
      transition: background-color 0.4s ease, color 0.4s ease;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .dark-theme {
      background-color: #121212;
      color: #ddd;
    }
    a {
      color: inherit;
      text-decoration: none;
    }
    a:hover,a:focus {
      text-decoration: underline;
    }
    nav {
      background: #ffffffdd;
      box-shadow: 0 2px 8px rgb(0 0 0 / 0.1);
      padding: 0.5rem 1rem;
      position: sticky;
      top: 0;
      z-index: 1000;
      backdrop-filter: saturate(180%) blur(10px);
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
    }
    nav.dark-theme {
      background: #1f1f1fdd;
      box-shadow: 0 2px 8px rgb(255 255 255 / 0.1);
    }
    nav .brand {
      font-weight: 700;
      font-size: 1.5rem;
      color: #0077cc;
      user-select: none;
      display: flex;
      align-items: center;
    }
    nav .brand i {
      margin-right: 0.5rem;
      color: #0099ff;
    }
    nav .nav-links {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    nav .nav-links a {
      font-weight: 600;
      padding: 0.3rem 0.6rem;
      border-radius: 8px;
      transition: background-color 0.3s ease, color 0.3s ease;
      user-select: none;
    }
    nav .nav-links a:hover, nav .nav-links a:focus {
      background-color: #0077cc;
      color: white;
    }
    nav.dark-theme .nav-links a:hover, nav.dark-theme .nav-links a:focus {
      background-color: #0099ff;
      color: #000;
    }
    nav .theme-toggle-btn {
      cursor: pointer;
      background: none;
      border: 2px solid #0077cc;
      color: #0077cc;
      padding: 0.4rem 0.7rem;
      font-weight: 600;
      border-radius: 20px;
      transition: all 0.3s ease;
      user-select: none;
      font-size: 0.9rem;
    }
    nav .theme-toggle-btn:hover, nav .theme-toggle-btn:focus {
      background-color: #0077cc;
      color: white;
    }
    nav.dark-theme .theme-toggle-btn {
      border-color: #0099ff;
      color: #0099ff;
    }
    nav.dark-theme .theme-toggle-btn:hover, nav.dark-theme .theme-toggle-btn:focus {
      background-color: #0099ff;
      color: #000;
    }

    main.container {
      flex: 1 0 auto;
      max-width: 1100px;
      margin: 2rem auto 3rem;
      padding: 0 1rem;
      width: 100%;
    }

    h1.page-title {
      font-weight: 700;
      font-size: 2.4rem;
      margin-bottom: 1rem;
      user-select: none;
      color: #0077cc;
    }

    .tools-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill,minmax(220px,1fr));
      gap: 1.5rem;
      margin-top: 1rem;
    }
    .tool-card {
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgb(0 0 0 / 0.07);
      padding: 1.2rem;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      user-select: none;
      text-decoration: none;
    }
    nav.dark-theme .tool-card {
      background: #222;
      box-shadow: 0 4px 12px rgb(255 255 255 / 0.07);
    }
    .tool-card:hover,
    .tool-card:focus-within {
      transform: translateY(-6px);
      box-shadow: 0 15px 30px rgb(0 0 0 / 0.15);
      outline: none;
    }
    .tool-icon {
      font-size: 3.5rem;
      margin-bottom: 0.7rem;
      color: #0077cc;
      transition: color 0.3s ease;
    }
    nav.dark-theme .tool-icon {
      color: #0099ff;
    }
    .tool-name {
      font-weight: 700;
      font-size: 1.2rem;
      text-align: center;
      color: inherit;
      user-select: none;
    }
    .tool-desc {
      font-size: 0.9rem;
      margin-top: 0.3rem;
      color: #555;
      text-align: center;
    }
    nav.dark-theme .tool-desc {
      color: #bbb;
    }

    form.upload-form {
      max-width: 400px;
      margin-top: 2rem;
      background: white;
      border-radius: 12px;
      padding: 1rem 1.5rem;
      box-shadow: 0 3px 12px rgb(0 0 0 / 0.1);
      position: relative;
      overflow: hidden;
    }
    nav.dark-theme form.upload-form {
      background: #222;
      box-shadow: 0 3px 12px rgb(255 255 255 / 0.1);
    }

    .file-input {
      width: 100%;
      padding: 0.6rem;
      font-size: 1rem;
      border: 2px solid #0077cc;
      border-radius: 8px;
      cursor: pointer;
      background: transparent;
      color: inherit;
      transition: border-color 0.3s ease;
      outline: none;
    }
    .file-input:hover,
    .file-input:focus {
      border-color: #004a99;
    }
    nav.dark-theme .file-input {
      border-color: #0099ff;
    }
    nav.dark-theme .file-input:hover,
    nav.dark-theme .file-input:focus {
      border-color: #005dbb;
    }

    button.submit-btn {
      margin-top: 1rem;
      width: 100%;
      background-color: #0077cc;
      border: none;
      color: white;
      font-size: 1.1rem;
      font-weight: 700;
      padding: 0.7rem;
      border-radius: 20px;
      cursor: pointer;
      user-select: none;
      transition: background-color 0.3s ease;
      position: relative;
      overflow: hidden;
    }
    button.submit-btn:hover,
    button.submit-btn:focus {
      background-color: #005a99;
    }
    nav.dark-theme button.submit-btn {
      background-color: #0099ff;
    }
    nav.dark-theme button.submit-btn:hover,
    nav.dark-theme button.submit-btn:focus {
      background-color: #007acc;
    }

    .flash-message {
      margin-top: 1rem;
      padding: 0.8rem 1rem;
      background-color: #d4edda;
      border-color: #c3e6cb;
      color: #155724;
      border-radius: 8px;
      font-weight: 600;
      user-select: none;
      text-align: center;
      animation: fadeIn 1s ease forwards;
    }
    nav.dark-theme .flash-message {
      background-color: #2f6e3a;
      border-color: #2f6e3a;
      color: #c9f9b5;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(0, 119, 204, 0.7);}
      70% { box-shadow: 0 0 0 10px rgba(0, 119, 204, 0);}
      100% { box-shadow: 0 0 0 0 rgba(0, 119, 204, 0);}
    }

    .uploading {
      animation: pulse 1.5s infinite;
    }

    @keyframes fadeIn {
      from {opacity:0;}
      to {opacity:1;}
    }

    .loader {
      border: 3px solid #f3f3f3; 
      border-top: 3px solid #0077cc; 
      border-radius: 50%;
      width: 20px;
      height: 20px;
      animation: spin 1s linear infinite;
      display: inline-block;
      vertical-align: middle;
      margin-left: 10px;
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    .loader.visible {
      opacity: 1;
    }

    @keyframes spin {
      0% { transform: rotate(0deg);}
      100% { transform: rotate(360deg);}
    }

    .nav-menu {
      display: none;
      flex-direction: column;
      width: 100%;
      text-align: center;
      margin-top: 0.5rem;
    }
    .nav-menu.active {
      display: flex;
    }
    .nav-toggle {
      display: none;
      cursor: pointer;
      font-size: 1.5rem;
      background: none;
      border: none;
      color: inherit;
    }
    @media(max-width: 768px) {
      nav .nav-links {
        display: none;
      }
      .nav-toggle {
        display: block;
      }
    }
  </style>
  {% block head %}{% endblock %}
</head>
<body>
<nav id="navbar" class="{% if dark_theme %}dark-theme{% endif %}">
  <div class="brand" aria-label="PAPERPREP Logo" tabindex="0"><i class="fas fa-file-alt"></i> PAPERPREP</div>
  <button aria-label="Menu toggle" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="nav-menu">
    <i class="fas fa-bars"></i>
  </button>
  <div class="nav-links" id="nav-menu" role="menu">
    {% for item in nav_items %}
      <a href="{{ url_for(item.endpoint) }}" role="menuitem" tabindex="0">{{ item.name }}</a>
    {% endfor %}
  </div>
  <button class="theme-toggle-btn" id="theme-toggle-btn" aria-pressed="false" aria-label="Toggle dark theme">Dark Theme</button>
</nav>

<main class="container">
  {{ content | safe }}
</main>

<script>
  const btn = document.getElementById('theme-toggle-btn');
  const body = document.body;
  const nav = document.getElementById('navbar');
  const navMenu = document.getElementById('nav-menu');
  const navToggle = document.getElementById('nav-toggle');

  if (localStorage.getItem('dark-theme') === 'true') {
    body.classList.add('dark-theme');
    nav.classList.add('dark-theme');
    btn.textContent = 'Light Theme';
    btn.setAttribute('aria-pressed', 'true');
  }

  btn.addEventListener('click', () => {
    const darkMode = body.classList.toggle('dark-theme');
    nav.classList.toggle('dark-theme');
    if(darkMode) {
      btn.textContent = 'Light Theme';
      btn.setAttribute('aria-pressed', 'true');
    } else {
      btn.textContent = 'Dark Theme';
      btn.setAttribute('aria-pressed', 'false');
    }
    localStorage.setItem('dark-theme', darkMode);
  });

  navToggle.addEventListener('click', () => {
    const expanded = navToggle.getAttribute('aria-expanded') === 'true' || false;
    navToggle.setAttribute('aria-expanded', !expanded);
    navMenu.classList.toggle('active');
  });

  function animateUpload(button) {
    button.disabled = true;
    button.classList.add('uploading');
    button.textContent = 'Uploading';
    const loader = document.createElement('span');
    loader.className = 'loader visible';
    button.appendChild(loader);
  }

  function uploadComplete(button) {
    button.disabled = false;
    button.classList.remove('uploading');
    button.textContent = 'Success ✓';
    setTimeout(() => {
      button.textContent = 'Upload';
    }, 2000);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('.upload-form');
    forms.forEach(form => {
      form.addEventListener('submit', event => {
        event.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        animateUpload(submitBtn);

        const formData = new FormData(form);

        fetch(form.action, {
          method: 'POST',
          body: formData
        }).then(resp => {
          if(resp.ok) {
            return resp.blob().then(blob => {
              let disposition = resp.headers.get('Content-Disposition');
              let filename = 'converted_file';
              if(disposition && disposition.indexOf('filename=') !== -1) {
                let match = disposition.match(/filename="?([^"]+)"?/);
                if(match) filename = match[1];
              }
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = filename;
              document.body.appendChild(a);
              a.click();
              a.remove();
              window.URL.revokeObjectURL(url);
              uploadComplete(submitBtn);
            });
          } else {
            resp.json().then(data => {
              alert('Conversion failed: ' + (data.error || 'Unknown error'));
              submitBtn.disabled = false;
              submitBtn.classList.remove('uploading');
              submitBtn.textContent = 'Upload';
            });
          }
        }).catch(err => {
          alert('Error during upload/conversion: ' + err);
          submitBtn.disabled = false;
          submitBtn.classList.remove('uploading');
          submitBtn.textContent = 'Upload';
        });
      });
    });
  });
</script>
{% block scripts %}{% endblock %}
</body>
</html>
'''

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def render_page(page_title, content):
    return render_template_string(BASE_HTML, page_title=page_title, content=content,
                                  nav_items=NAV_ITEMS, dark_theme=False)

@app.route('/')
def home():
    items_html = '<h1 class="page-title">Welcome to PAPERPREP</h1>'
    items_html += '<p style="max-width:600px; color:#555;">Explore our powerful and fast file conversion and compression tools. Click on any tool to get started.</p>'
    items_html += '<div class="tools-grid" role="list">'
    for tool in TOOLS:
        items_html += f'''<a href="{url_for(tool['endpoint'])}" class="tool-card" role="listitem" tabindex="0" aria-label="{tool['name']}">
            <i class="{tool['icon']} tool-icon" aria-hidden="true"></i>
            <div class="tool-name">{tool['name']}</div>
            <div class="tool-desc">{tool['description']}</div>
        </a>'''
    items_html += '</div>'
    return render_page('Home', items_html)


def tool_page_html(tool, success_msg=None):
    accepted_ext_list = ", ".join(tool['accepted'])
    multiple = 'multiple' if tool['endpoint'] in ['images_to_pdf', 'merge_pdf'] else ''
    multiple_bool = tool['endpoint'] in ['images_to_pdf', 'merge_pdf']
    form_html = f'''
    <h1 class="page-title">{tool['name']}</h1>
    <p>{tool['description']}</p>
    <p><b>Accepted file types:</b> {accepted_ext_list}</p>
    <form class="upload-form" method="POST" enctype="multipart/form-data" aria-label="Upload file form" action="{url_for(tool['endpoint'])}">
      <label for="file" style="font-weight:600; margin-bottom:0.5rem; display:block;">Choose file{'s' if multiple_bool else ''}</label>
      <input class="file-input" type="file" name="file" id="file" accept="{','.join(['.'+e for e in tool['accepted']])}" {multiple} required aria-required="true"/>
      <button type="submit" class="submit-btn" aria-live="polite">Upload</button>
    </form>
    '''
    if success_msg:
        form_html += f'<div class="flash-message" role="alert" aria-live="assertive">{success_msg}</div>'
    return render_page(tool['name'], form_html)

def pdf_to_word_convert(input_path, output_path):
    converter = Converter(input_path)
    converter.convert(output_path, start=0, end=None)
    converter.close()

def jpg_to_word_convert(input_path, output_path):
    img = Image.open(input_path)
    text = pytesseract.image_to_string(img)
    doc = Document()
    doc.add_paragraph(text)
    doc.save(output_path)

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

for tool in TOOLS:
    endpoint = tool['endpoint']

    def make_route(tool=tool):
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
                    if tool['endpoint'] in ['jpg_to_word', 'pdf_to_word']:
                        out_filename += ".docx"
                    elif tool['endpoint'] in ['ppt_to_pdf', 'images_to_pdf', 'merge_pdf', 'pdf_compressor']:
                        out_filename += ".pdf"
                    elif tool['endpoint'] == 'pdf_to_ppt':
                        out_filename += ".pptx"
                    elif tool['endpoint'] == 'image_compressor':
                        ext = os.path.splitext(input_paths[0])[1].lower()
                        out_filename += ext
                    else:
                        out_filename += ".out"

                    out_path = os.path.join(tempfile.mkdtemp(), out_filename)

                    if tool['endpoint'] == 'pdf_to_word':
                        pdf_to_word_convert(input_paths[0], out_path)
                    elif tool['endpoint'] == 'jpg_to_word':
                        jpg_to_word_convert(input_paths[0], out_path)
                    elif tool['endpoint'] == 'ppt_to_pdf':
                        return jsonify({'error': 'PPT to PDF conversion requires external tools not supported here.'}), 400
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
        tool_func.__name__ = endpoint
        tool_func.methods = ['GET', 'POST']
        return tool_func

    app.add_url_rule(f'/{endpoint}', view_func=make_route(), methods=['GET', 'POST'])


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
