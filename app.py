import os
import io
import tempfile
from flask import Flask, request, redirect, url_for, flash, render_template_string, send_file, jsonify
from werkzeug.utils import secure_filename

from docx import Document
from docx.shared import Inches
from PIL import Image

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
</head>
<body>
<nav id="navbar" class="">
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
</body>
</html>
'''

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def render_page(page_title, content):
    from flask import render_template_string
    return render_template_string(BASE_HTML, page_title=page_title, content=content,
                                  nav_items=NAV_ITEMS, dark_theme=False)

@app.route('/')
def home():
    items_html = '<h1 class="page-title">Welcome to PAPERPREP</h1>'
    items_html += '<p style="max-width:600px; color:#555;">Explore powerful and fast file conversion tools. Click any tool to start.</p>'
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

def jpg_to_word_convert(input_path, output_path):
    img = Image.open(input_path)
    doc = Document()
    # Insert image into Word doc with reasonable width (max 6 inches)
    doc.add_picture(input_path, width=Inches(6))
    doc.save(output_path)

# Dummy placeholder functions for other conversions (real implementations should be here)
def pdf_to_word_convert(input_path, output_path):
    with open(output_path, 'wb') as f:
        f.write(b'This is a dummy PDF to word conversion file.')

def ppt_to_pdf_convert(input_path, output_path):
    pass

def pdf_to_ppt_convert(input_path, output_path):
    pass

def images_to_pdf_convert(input_paths, output_path):
    pass

def merge_pdfs(input_paths, output_path):
    pass

def image_compress(input_path, output_path):
    pass

def pdf_compress(input_path, output_path):
    pass

def save_upload(file_storage):
    filename = secure_filename(file_storage.filename)
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, filename)
    file_storage.save(file_path)
    return file_path, temp_dir, filename

import shutil

# For this demo we'll implement only jpg_to_word properly
def endpoint_route(tool):
    def route_func():
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
                if tool['endpoint'] == 'jpg_to_word':
                    out_filename += ".docx"
                else:
                    out_filename += ".out"

                out_path = os.path.join(tempfile.mkdtemp(), out_filename)

                if tool['endpoint'] == 'jpg_to_word':
                    jpg_to_word_convert(input_paths[0], out_path)
                else:
                    return jsonify({'error': 'Tool not implemented yet.'}), 400

                return send_file(out_path, as_attachment=True, download_name=out_filename)
            finally:
                for d in temp_dirs:
                    shutil.rmtree(d, ignore_errors=True)
        return tool_page_html(tool)
    route_func.__name__ = tool['endpoint']
    route_func.methods = ['GET', 'POST']
    return route_func

for tool in TOOLS:
    if tool['endpoint'] == 'jpg_to_word':
        app.add_url_rule(f'/{tool["endpoint"]}', view_func=endpoint_route(tool), methods=['GET', 'POST'])
    else:
        # Add dummy routes for other tools that return not implemented
        def dummy_route(tool=tool):
            def f():
                return f"<h1>{tool['name']}</h1><p>Tool not implemented yet.</p>"
            f.__name__ = tool['endpoint']
            return f
        app.add_url_rule(f'/{tool["endpoint"]}', view_func=dummy_route(), methods=['GET', 'POST'])

@app.route('/about')
def about():
    content = (
        "PAPERPREP is a fast, efficient, and futuristic file conversion web application designed "
        "for all your document needs. Built with cutting-edge technology and a sleek UI for an "
        "awesome user experience."
    )
    return render_page('About', f'<h1 class="page-title">About</h1><p>{content}</p>')

@app.route('/privacy')
def privacy():
    content = (
        "Your privacy is important to us. We do not store your uploaded files or share any data. "
        "All processing is done securely and temporarily."
    )
    return render_page('Privacy Policy', f'<h1 class="page-title">Privacy Policy</h1><p>{content}</p>')

@app.route('/contact')
def contact():
    content = (
        "Contact us at:\n\n"
        "Email: support@paperprep.com\n"
        "Phone: +1 234 567 8900\n"
        "Address: 123 College St, City, Country"
    )
    return render_page('Contact', f'<h1 class="page-title">Contact</h1><pre>{content}</pre>')

@app.route('/terms')
def terms():
    content = (
        "Terms and Conditions:\n\n"
        "Use PAPERPREP at your own risk. We strive to provide accurate conversions but "
        "do not guarantee results. By using the service, you accept our terms."
    )
    return render_page('Terms and Conditions', f'<h1 class="page-title">Terms and Conditions</h1><pre>{content}</pre>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
