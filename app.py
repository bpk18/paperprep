import io
import os
import tempfile
from flask import Flask, send_file, request, render_template_string, abort, redirect, url_for
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from PIL import Image
import pytesseract
from pptx import Presentation
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__, static_folder='static')

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}
ALLOWED_PPT_EXTENSIONS = {'ppt', 'pptx'}

def allowed_file(filename, allowed_exts):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


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
      display: flex;
      align-items: center;
      gap: 0.75rem;
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
      cursor: pointer;
      user-select: none;
    }
    .card:hover,
    .card:focus {
      box-shadow: 0 5px 20px rgb(0 0 0 / 0.15);
      transform: translateY(-3px);
      outline: none;
    }
    body.dark .card {
      background-color: #222;
      box-shadow: 0 2px 10px rgba(255 255 255 / 0.05);
    }
    body.dark .card:hover,
    body.dark .card:focus {
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
      user-select:none;
    }
    body.dark .card-desc {
      color: #bbb;
    }
    /* Dropdown menu */
    .dropdown {
      position: relative;
      display: inline-block;
    }
    .dropdown-button {
      background: transparent;
      border: none;
      font-size: 1.75rem;
      cursor: pointer;
      color: var(--color-primary);
      padding: 0;
      user-select: none;
    }
    body.dark .dropdown-button {
      color: var(--color-primary-light);
    }
    .dropdown-menu {
      position: absolute;
      top: 150%;
      right: 0;
      background-color: #fff;
      border-radius: 6px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.2);
      min-width: 160px;
      display: none;
      flex-direction: column;
      z-index: 1500;
    }
    body.dark .dropdown-menu {
      background-color: #1e1e1e;
      box-shadow: 0 2px 12px rgba(255,255,255,0.1);
    }
    .dropdown-menu.open {
      display: flex;
    }
    .dropdown-menu button {
      background: none;
      border: none;
      padding: 10px 16px;
      text-align: left;
      width: 100%;
      font-weight: 600;
      color: var(--color-primary);
      cursor: pointer;
      font-size: 1rem;
      user-select: none;
    }
    body.dark .dropdown-menu button {
      color: var(--color-primary-light);
    }
    .dropdown-menu button:hover, .dropdown-menu button:focus {
      background-color: var(--color-accent);
      color: white;
      outline: none;
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
        <li><a href="{{ url_for('tool_page', tool='pdf-to-word') }}" role="menuitem" tabindex="0">PDF to Word</a></li>
        <li><a href="{{ url_for('tool_page', tool='jpg-to-word') }}" role="menuitem" tabindex="0">JPG to Word</a></li>
        <li><a href="{{ url_for('tool_page', tool='ppt-to-pdf') }}" role="menuitem" tabindex="0">PPT to PDF</a></li>
        <li><a href="{{ url_for('tool_page', tool='pdf-to-ppt') }}" role="menuitem" tabindex="0">PDF to PPT</a></li>
        <li><a href="{{ url_for('tool_page', tool='multiple-images-to-pdf') }}" role="menuitem" tabindex="0">Multiple Images to PDF</a></li>
        <li><a href="{{ url_for('tool_page', tool='merge-pdf') }}" role="menuitem" tabindex="0">Merge PDF</a></li>
        <li><a href="{{ url_for('tool_page', tool='image-compressor') }}" role="menuitem" tabindex="0">Image Compressor</a></li>
        <li><a href="{{ url_for('tool_page', tool='pdf-compressor') }}" role="menuitem" tabindex="0">PDF Compressor</a></li>
        <li>
          <div class="dropdown">
            <button class="dropdown-button" aria-haspopup="true" aria-expanded="false" aria-label="Open info menu">&#8942;</button>
            <div class="dropdown-menu" role="menu" aria-label="Information menu">
              <button role="menuitem" class="info-menu-btn" data-info="about">About</button>
              <button role="menuitem" class="info-menu-btn" data-info="privacy">Privacy</button>
              <button role="menuitem" class="info-menu-btn" data-info="contact">Contact</button>
              <button role="menuitem" class="info-menu-btn" data-info="terms">Terms & Conditions</button>
            </div>
          </div>
        </li>
      </ul>
    </nav>
    <button class="theme-toggle" aria-label="Toggle dark mode">Dark Theme</button>
  </header>

  <main>
    <h1 style="text-align:center;">Welcome to PAPERPREP</h1>
    <p style="max-width:600px; margin:0 auto 2rem auto; text-align:center; color:#555;">
      Your all-in-one futuristic file conversion and compression toolkit. Quickly convert, compress, and manage your documents and images.
    </p>
    <div class="tools-grid" role="list" aria-label="List of conversion and compression tools">
      <article class="card" role="listitem" tabindex="0" onclick="location.href='{{ url_for('tool_page', tool='pdf-to-word') }}';" onkeypress="if(event.key==='Enter'){location.href='{{ url_for('tool_page', tool='pdf-to-word') }}';}">
        <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64" >
          <path d="M48 2H16C12.7 2 10 4.7 10 8V56C10 59.3 12.7 62 16 62H48C51.3 62 54 59.3 54 56V8C54 4.7 51.3 2 48 2Z" />
          <path d="M28 18H36V46H28Z" fill="#f4a261"/>
          <path d="M36 24L44 18" stroke="#5c6ac4" stroke-width="2"/>
        </svg>
        <h3 class="card-title">PDF to Word</h3>
        <p class="card-desc">Convert your PDF documents to editable Word files.</p>
      </article>
      <!-- Repeat for other tools as before -->
      <!-- ... -->
    </div>
  </main>

  <footer>
    &copy; 2024 PAPERPREP. All rights reserved.
  </footer>

  <!-- Modal for info content -->
  <div id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" tabindex="-1" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.5); align-items:center; justify-content:center; z-index:2000;">
    <div id="modal-content" style="max-width:600px; background:#fff; border-radius:12px; padding:1.5rem 2rem; color:#222; overflow-y:auto; max-height:80vh; position:relative;">
      <button id="modal-close" aria-label="Close dialog" style="position:absolute; top:12px; right:16px; background:none; border:none; font-size:1.5rem; cursor:pointer; color:inherit;">&times;</button>
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
    document.addEventListener('click', (e) => {
      if (!menu.contains(e.target) && !menuToggle.contains(e.target)) {
        menu.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', false);
      }
    });

    // Dropdown menu toggle
    const dropdownButton = document.querySelector('.dropdown-button');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    dropdownButton.addEventListener('click', (e) => {
      e.stopPropagation();
      const expanded = dropdownButton.getAttribute('aria-expanded') === 'true' || false;
      dropdownButton.setAttribute('aria-expanded', !expanded);
      dropdownMenu.classList.toggle('open');
    });
    document.addEventListener('click', () => {
      dropdownMenu.classList.remove('open');
      dropdownButton.setAttribute('aria-expanded', false);
    });

    // Theme toggle
    const themeToggleBtn = document.querySelector('.theme-toggle');
    const bodyElement = document.body;
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
      button.addEventListener('click', (e) => {
        e.stopPropagation();
        const key = button.getAttribute('data-info');
        if (infoContents[key]) {
          modalTitle.innerHTML = infoContents[key].title;
          modalBody.innerHTML = infoContents[key].content;
          modal.style.display = 'flex';
          modal.focus();
          // Close dropdown menu
          dropdownMenu.classList.remove('open');
          dropdownButton.setAttribute('aria-expanded', false);
        }
      });
    });
    modalCloseBtn.addEventListener('click', () => {
      modal.style.display = 'none';
    });
    document.addEventListener('keydown', (e) => {
      if(e.key === 'Escape' && modal.style.display === 'flex'){
        modal.style.display = 'none';
      }
    });
  </script>
</body>
</html>
"""

# TOOL_PAGES dict and TOOL_PAGE_HTML_TEMPLATE same as previous implementation, omitted for brevity but unchanged

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

# The rest of app.py including tool_page route and backend convert endpoints remain the same as previous implementation,
# so omitted here for brevity.

# Route for favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(app.static_folder, 'favicon.ico'))

if __name__ == '__main__':
    # Run app on all interfaces, port 5000 with debug
    app.run(host='0.0.0.0', port=5000, debug=True)
