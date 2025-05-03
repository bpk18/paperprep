"""
PAPERPREP Flask Application

Requirements:
- Python 3.7+
- Install dependencies:
    pip install flask pdf2docx python-pptx Pillow pytesseract PyPDF2 reportlab python-docx

Note:
- pytesseract requires the Tesseract OCR engine installed separately:
  MacOS (Homebrew): brew install tesseract
  Windows: see https://github.com/tesseract-ocr/tesseract
  Linux: sudo apt-get install tesseract-ocr

Run server:
  python app.py
"""

import os
import tempfile
from flask import Flask, send_file, request, render_template_string, abort
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
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9764517671001230"
     crossorigin="anonymous"></script>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
  <meta name="description" content="PAPERPREP: Futuristic file conversion and compression tools for PDFs, images, presentations, and more. Clean, responsive UI." />
  <meta name="keywords" content="file converter, file compressor, PAPERPREP" />
  <meta name="author" content="PAPERPREP Team" />
  <meta name="robots" content="index, follow" />
  <title>PAPERPREP - Futuristic File Conversion & Compression Tools</title>
  <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon" />
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body {
      margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f0f4f8; color: #222; min-height: 100vh;
      display: flex; flex-direction: column;
    }
    h1{
    text-align:center;
    }
    :root {
      --color-primary: #5c6ac4;
      --color-primary-light: #8c97f9;
      --color-accent: #f4a261;
      --color-bg-dark: #121212;
      --color-text-dark: #ddd;
      --color-button-bg: var(--color-primary);
      --color-button-text: #fff;
      --color-button-hover-bg: var(--color-primary-light);
    }
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
    header {
      background-color: #fff;
      padding: 1rem;
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
    /* Hide traditional menu links */
    ul.menu li a {
      display: none;
    }
    body.dark ul.menu li a {
      display: none;
    }
    /* Media query for hamburger menu */
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
      font-size: 1.1rem;
    }
    .theme-toggle:hover,
    .theme-toggle:focus {
      background-color: var(--color-button-hover-bg);
      outline: none;
    }
    main {
      flex-grow: 1;
      padding: 3rem 1rem;
      max-width: 900px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 3rem;
    }
    .tools-grid {
      display: grid;
      gap: 2rem;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }
    .card {
      background-color: #fff;
      border-radius: 20px;
      padding: 2rem;
      box-shadow: 0 6px 15px rgb(0 0 0 / 0.15);
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
      box-shadow: 0 12px 40px rgb(0 0 0 / 0.25);
      transform: translateY(-6px);
      outline: none;
    }
    body.dark .card {
      background-color: #222;
      box-shadow: 0 6px 15px rgba(255 255 255 / 0.07);
    }
    body.dark .card:hover,
    body.dark .card:focus {
      box-shadow: 0 12px 40px rgba(255 255 255 / 0.15);
    }
    .card-icon {
      width: 80px;
      height: 80px;
      margin-bottom: 1.5rem;
      fill: var(--color-primary);
      transition: fill 0.3s;
    }
    body.dark .card-icon {
      fill: var(--color-primary-light);
    }
    .card-title {
      font-size: 1.5rem;
      font-weight: 800;
      margin-bottom: 0.75rem;
      user-select:none;
    }
    .card-desc {
      font-size: 1rem;
      color: #555;
      margin-bottom: 1.25rem;
    }
    body.dark .card-desc {
      color: #bbb;
    }
    .dropdown {
      position: relative;
      display: inline-block;
    }
    .dropdown-button {
      background: transparent;
      border: none;
      font-size: 2rem;
      cursor: pointer;
      color: var(--color-primary);
      padding: 0;
      margin-left: 1rem;
      user-select: none;
    }
    body.dark .dropdown-button {
      color: var(--color-primary-light);
    }
    .dropdown-menu {
      position: absolute;
      top: 160%;
      right: 0;
      background-color: #fff;
      border-radius: 10px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.25);
      min-width: 180px;
      display: none;
      flex-direction: column;
      z-index: 1500;
      padding: 0.5rem 0;
    }
    body.dark .dropdown-menu {
      background-color: #1e1e1e;
      box-shadow: 0 4px 24px rgba(255 255 255, 0.12);
    }
    .dropdown-menu.open {
      display: flex;
    }
    .dropdown-menu button {
      background: none;
      border: none;
      padding: 12px 20px;
      text-align: left;
      width: 100%;
      font-weight: 600;
      color: var(--color-primary);
      cursor: pointer;
      font-size: 1rem;
      transition: background-color 0.25s;
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
    footer {
      text-align: center;
      padding: 1.25rem;
      font-size: 1rem;
      color: #888;
      user-select:none;
    }
    body.dark footer {
      color: #555;
    }
  </style>
</head>
<body>
  <header>
    <div class="logo" aria-label="PAPERPREP">PAPERPREP</div>
    <nav aria-label="Main navigation and info menu">
      <button class="menu-toggle" aria-label="Toggle menu" aria-expanded="false" aria-controls="main-menu">
      </button>
      <ul class="menu" id="main-menu" role="menu">
        <!-- No links shown in nav -->
        <li>
          <div class="dropdown">
            <button class="dropdown-button" aria-haspopup="true" aria-expanded="false" aria-label="Open information menu">&#8942;</button>
            <div class="dropdown-menu" role="menu" aria-label="Information menu">
              <button role="menuitem" class="info-menu-btn" data-info="about">About</button>
              <button role="menuitem" class="info-menu-btn" data-info="privacy">Privacy</button>
              <button role="menuitem" class="info-menu-btn" data-info="contact">Contact</button>
              <button role="menuitem" class="info-menu-btn" data-info="terms">Terms &amp; Conditions</button>
            </div>
          </div>
        </li>
      </ul>
    </nav>
    <button class="theme-toggle" aria-label="Toggle dark mode">Dark Theme</button>
  </header>

  <main>
    <h1>Welcome to PAPERPREP</h1>
    <p style="max-width:600px; margin:0 auto 3rem; text-align:center; color:#475767; font-size: 1.15rem;">
      Your futuristic file conversion and compression toolkit. Select a tool below to get started.
    </p>
    <div class="tools-grid" role="list" aria-label="Conversion and compression tools">
      <article class="card" role="listitem" tabindex="0" aria-label="PDF to Word" onclick="window.location.href='{{ url_for('tool_page', tool='pdf-to-word') }}';" onkeypress="if(event.key==='Enter'){window.location.href='{{ url_for('tool_page', tool='pdf-to-word') }}';}">
        <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64" >
          <path d="M48 2H16C12.7 2 10 4.7 10 8V56C10 59.3 12.7 62 16 62H48C51.3 62 54 59.3 54 56V8C54 4.7 51.3 2 48 2Z"/>
          <path d="M28 18H36V46H28Z" fill="#f4a261"/>
          <path d="M36 24L44 18" stroke="#5c6ac4" stroke-width="2"/>
        </svg>
        <h3 class="card-title">PDF to Word</h3>
        <p class="card-desc">Convert your PDF documents to editable Word files.</p>
      </article>
      <article class="card" role="listitem" tabindex="0" aria-label="JPG to Word" onclick="window.location.href='{{ url_for('tool_page', tool='jpg-to-word') }}';" onkeypress="if(event.key==='Enter'){window.location.href='{{ url_for('tool_page', tool='jpg-to-word') }}';}">
        <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64" >
          <circle cx="32" cy="32" r="30" fill="#8c97f9"/>
          <rect x="15" y="22" width="34" height="20" rx="4" ry="4" fill="#61a5c2"/>
          <circle cx="32" cy="32" r="8" fill="#f4a261"/>
        </svg>
        <h3 class="card-title">JPG to Word</h3>
        <p class="card-desc">Extract text from your JPG images into Word format.</p>
      </article>
      <article class="card" role="listitem" tabindex="0" aria-label="PPT to PDF" onclick="window.location.href='{{ url_for('tool_page', tool='ppt-to-pdf') }}';" onkeypress="if(event.key==='Enter'){window.location.href='{{ url_for('tool_page', tool='ppt-to-pdf') }}';}">
        <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
          <rect x="14" y="10" width="36" height="44" rx="6" ry="6" fill="#5c6ac4"/>
          <rect x="20" y="18" width="24" height="28" fill="#f4a261"/>
          <rect x="20" y="22" width="24" height="6" fill="#fff"/>
          <rect x="20" y="34" width="24" height="6" fill="#fff"/>
        </svg>
        <h3 class="card-title">PPT to PDF</h3>
        <p class="card-desc">Easily convert your PowerPoint presentations to PDF files.</p>
      </article>
      <article class="card" role="listitem" tabindex="0" aria-label="PDF to PPT" onclick="window.location.href='{{ url_for('tool_page', tool='pdf-to-ppt') }}';" onkeypress="if(event.key==='Enter'){window.location.href='{{ url_for('tool_page', tool='pdf-to-ppt') }}';}">
        <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
          <path d="M10 54L54 10" stroke="#5c6ac4" stroke-width="5" stroke-linecap="round"/>
          <circle cx="22" cy="22" r="10" fill="#f4a261"/>
          <circle cx="42" cy="42" r="10" fill="#61a5c2"/>
          <text x="22" y="26" font-size="10" text-anchor="middle" fill="#fff" font-family="Segoe UI">PPT</text>
          <text x="42" y="46" font-size="10" text-anchor="middle" fill="#fff" font-family="Segoe UI">PDF</text>
        </svg>
        <h3 class="card-title">PDF to PPT</h3>
        <p class="card-desc">Convert PDF documents back to editable PowerPoint presentations.</p>
      </article>
      <article class="card" role="listitem" tabindex="0" aria-label="Multiple Images into One PDF" onclick="window.location.href='{{ url_for('tool_page', tool='multiple-images-to-pdf') }}';" onkeypress="if(event.key==='Enter'){window.location.href='{{ url_for('tool_page', tool='multiple-images-to-pdf') }}';}">
        <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
          <rect x="8" y="12" width="20" height="40" rx="4" ry="4" fill="#5c6ac4"/>
          <rect x="36" y="12" width="20" height="40" rx="4" ry="4" fill="#61a5c2"/>
          <path d="M16 26H44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
          <path d="M16 38H44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
        </svg>
        <h3 class="card-title">Multiple Images into One PDF</h3>
        <p class="card-desc">Combine multiple images into a single PDF file easily.</p>
      </article>
      <article class="card" role="listitem" tabindex="0" aria-label="Merge PDF" onclick="window.location.href='{{ url_for('tool_page', tool='merge-pdf') }}';" onkeypress="if(event.key==='Enter'){window.location.href='{{ url_for('tool_page', tool='merge-pdf') }}';}">
        <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
          <rect x="12" y="14" width="40" height="36" rx="6" ry="6" fill="#5c6ac4"/>
          <path d="M16 20L48 44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
          <path d="M48 20L16 44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
        </svg>
        <h3 class="card-title">Merge PDF</h3>
        <p class="card-desc">Combine multiple PDF files into one seamless document.</p>
      </article>
      <article class="card" role="listitem" tabindex="0" aria-label="Image Compressor" onclick="window.location.href='{{ url_for('tool_page', tool='image-compressor') }}';" onkeypress="if(event.key==='Enter'){window.location.href='{{ url_for('tool_page', tool='image-compressor') }}';}">
        <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
          <circle cx="32" cy="32" r="26" stroke="#5c6ac4" stroke-width="4" fill="#61a5c2"/>
          <path d="M20 32H44" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
          <path d="M32 20V44" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
        </svg>
        <h3 class="card-title">Image Compressor</h3>
        <p class="card-desc">Compress images to reduce file size without losing quality.</p>
      </article>
      <article class="card" role="listitem" tabindex="0" aria-label="PDF Compressor" onclick="window.location.href='{{ url_for('tool_page', tool='pdf-compressor') }}';" onkeypress="if(event.key==='Enter'){window.location.href='{{ url_for('tool_page', tool='pdf-compressor') }}';}">
        <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
          <rect x="14" y="18" width="36" height="28" rx="6" ry="6" fill="#5c6ac4"/>
          <path d="M22 26H42" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
          <path d="M22 38H42" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
        </svg>
        <h3 class="card-title">PDF Compressor</h3>
        <p class="card-desc">Reduce the size of your PDF files for faster sharing.</p>
      </article>
    </div>
  </main>

  <footer>&copy; 2024 PAPERPREP. All rights reserved.</footer>

  <!-- Modal -->
  <div id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" tabindex="-1" style="display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.5);align-items:center;justify-content:center;z-index:2000;">
    <div id="modal-content" style="max-width:600px;background:#fff;border-radius:12px;padding:1.5rem 2rem;color:#222;overflow-y:auto;max-height:80vh;position:relative;">
      <button id="modal-close" aria-label="Close dialog" style="position:absolute;top:12px;right:16px;background:none;border:none;font-size:1.5rem;cursor:pointer;color:inherit;">&times;</button>
      <h2 id="modal-title"></h2>
      <div id="modal-body"></div>
    </div>
  </div>

  <script>
    const menuToggle = document.querySelector('.menu-toggle');
    const menu = document.querySelector('.menu');
    menuToggle.addEventListener('click', () => {
      const expanded = menuToggle.getAttribute('aria-expanded') === 'true' || false;
      menuToggle.setAttribute('aria-expanded', !expanded);
      menu.classList.toggle('open');
    });
    document.addEventListener('click', e => {
      if (!menu.contains(e.target) && !menuToggle.contains(e.target)) {
        menu.classList.remove('open');
        menuToggle.setAttribute('aria-expanded', false);
      }
    });
    const dropdownButton = document.querySelector('.dropdown-button');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    dropdownButton.addEventListener('click', e => {
      e.stopPropagation();
      const expanded = dropdownButton.getAttribute('aria-expanded') === 'true' || false;
      dropdownButton.setAttribute('aria-expanded', !expanded);
      dropdownMenu.classList.toggle('open');
    });
    document.addEventListener('click', () => {
      dropdownMenu.classList.remove('open');
      dropdownButton.setAttribute('aria-expanded', false);
    });
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
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const modalCloseBtn = document.getElementById('modal-close');
    const infoContents = {
      about: { title: 'About PAPERPREP', content: `<p>PAPERPREP is an innovative platform designed to make file conversions and compression effortless and efficient. Whether you are a student, professional, or a casual user, our futuristic tools help you manage documents and images with just a few clicks. Our mission is to provide a seamless and intuitive user experience with cutting edge technology and soothing design.</p>` },
      privacy: { title: 'Privacy Policy', content: `<p>Your privacy is important to us. PAPERPREP does not store or share any of your files. All conversions occur securely and temporarily with no user data retention. We use industry best practices to safeguard your information.</p>` },
      contact: { title: 'Contact Us', content: `<p>If you have any questions, suggestions, or need support, feel free to reach out to us at <a href="mailto:support@paperprep.com">support@paperprep.com</a>. We value your feedback.</p>` },
      terms: { title: 'Terms &amp; Conditions', content: `<p>By using PAPERPREP, you agree to our terms and conditions. We provide our tools &quot;as is&quot; without warranties. Use the services responsibly and respect intellectual property rights.</p>` }
    };
    document.querySelectorAll('.info-menu-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        const key = btn.getAttribute('data-info');
        if (infoContents[key]) {
          modalTitle.innerHTML = infoContents[key].title;
          modalBody.innerHTML = infoContents[key].content;
          modal.style.display = 'flex';
          modal.focus();
          dropdownMenu.classList.remove('open');
          dropdownButton.setAttribute('aria-expanded', false);
        }
      });
    });
    modalCloseBtn.addEventListener('click', () => { modal.style.display = 'none'; });
    document.addEventListener('keydown', e => {
      if(e.key === 'Escape' && modal.style.display === 'flex') {
        modal.style.display = 'none';
      }
    });
  </script>
</body>
</html>
"""

TOOL_PAGE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
  <meta name="description" content="{{ description }}" />
  <meta name="keywords" content="PAPERPREP, {{ title }}, file conversion, file compression" />
  <meta name="author" content="PAPERPREP Team" />
  <meta name="robots" content="index, follow" />
  <title>PAPERPREP - {{ title }}</title>
  <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon" />
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f0f4f8;
      color: #222;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    :root {
      --color-primary: #5c6ac4;
      --color-primary-light: #8c97f9;
      --color-button-bg: var(--color-primary);
      --color-button-text: #fff;
      --color-button-hover-bg: var(--color-primary-light);
    }
    body.dark {
      background-color: #121212;
      color: #ddd;
    }
    body.dark button {
      background-color: var(--color-primary-light);
      color: #222;
    }
    body.dark button:hover, body.dark button:focus {
      background-color: var(--color-primary);
      color: #fff;
    }
    header {
      background-color: #fff;
      padding: 1rem;
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
    ul.menu li a:hover, ul.menu li a:focus {
      color: var(--color-primary-light);
      outline: none;
    }
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
      font-size: 1.1rem;
    }
    .theme-toggle:hover, .theme-toggle:focus {
      background-color: var(--color-button-hover-bg);
      outline: none;
    }
    main {
      flex-grow: 1;
      padding: 3rem 1rem;
      max-width: 600px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 2rem;
      text-align: center;
    }
    label {
      font-weight: 700;
      font-size: 1.1rem;
      margin-bottom: 0.3rem;
      user-select: none;
    }
    input[type="file"] {
      padding: 1rem;
      border-radius: 12px;
      border: 2px dashed var(--color-primary);
      background-color: #e8f0fe;
      cursor: pointer;
      transition: background-color 0.3s;
      max-width: 100%;
    }
    input[type="file"]:hover {
      background-color: #d0e2fd;
    }
    button.submit-btn {
      background-color: var(--color-button-bg);
      color: var(--color-button-text);
      padding: 1rem 2rem;
      border: none;
      border-radius: 30px;
      font-weight: 800;
      font-size: 1.25rem;
      cursor: pointer;
      user-select: none;
      transition: background-color 0.3s;
      box-shadow: 0 8px 20px rgba(92,106,196,.4);
    }
    button.submit-btn:hover, button.submit-btn:focus {
      background-color: var(--color-button-hover-bg);
      outline: none;
      box-shadow: 0 12px 40px rgba(92,106,196,.6);
    }
    body.dark button.submit-btn {
      background-color: var(--color-primary-light);
      color: var(--color-text-dark);
      box-shadow: 0 8px 20px rgba(140,151,249,.4);
    }
    body.dark button.submit-btn:hover, body.dark button.submit-btn:focus {
      background-color: var(--color-primary);
      color: #fff;
      box-shadow: 0 12px 40px rgba(140,151,249,.6);
    }
    a.back-link {
      text-align: left;
      display: inline-block;
      margin-bottom: 1rem;
      font-weight: 600;
      color: var(--color-primary);
      text-decoration: none;
      cursor: pointer;
    }
    a.back-link:hover, a.back-link:focus {
      color: var(--color-primary-light);
      outline: none;
    }
  </style>
</head>
<body>
  <header>
    <div class="logo"><a href="{{ url_for('index') }}" style="color:inherit; text-decoration:none;">PAPERPREP</a></div>
    <nav>
      <div class="dropdown">
        <button class="dropdown-button" aria-haspopup="true" aria-expanded="false" aria-label="Open information menu">&#8942;</button>
        <div class="dropdown-menu" role="menu" aria-label="Information menu">
          <button role="menuitem" class="info-menu-btn" data-info="about">About</button>
          <button role="menuitem" class="info-menu-btn" data-info="privacy">Privacy</button>
          <button role="menuitem" class="info-menu-btn" data-info="contact">Contact</button>
          <button role="menuitem" class="info-menu-btn" data-info="terms">Terms &amp; Conditions</button>
        </div>
      </div>
    </nav>
    <button class="theme-toggle" aria-label="Toggle dark mode">Dark Theme</button>
  </header>
  <main>
    <a href="{{ url_for('index') }}" class="back-link">&#8592; Back to Home</a>
    <h1>{{ title }}</h1>
    <p>{{ description }}</p>
    <form method="post" action="{{ endpoint }}" enctype="multipart/form-data" target="downloadFrame" aria-label="Upload file form for {{ title }}">
      <label for="fileinput">Upload {{ 'files' if multiple else 'file' }} (drag & drop or click to select)</label>
      <input id="fileinput" type="file" name="{{ 'files' if multiple else 'file' }}" accept="{{ accept }}" {{ 'multiple' if multiple else '' }} required />
      <button type="submit" class="submit-btn">Convert & Download</button>
    </form>
  </main>
  <footer>
    &copy; 2024 PAPERPREP. All rights reserved.
  </footer>
  <iframe name="downloadFrame" style="display:none;"></iframe>

  <script>
    const dropdownButton = document.querySelector('.dropdown-button');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    dropdownButton.addEventListener('click', e => {
      e.stopPropagation();
      const expanded = dropdownButton.getAttribute('aria-expanded') === 'true' || false;
      dropdownButton.setAttribute('aria-expanded', !expanded);
      dropdownMenu.classList.toggle('open');
    });
    document.addEventListener('click', () => {
      dropdownMenu.classList.remove('open');
      dropdownButton.setAttribute('aria-expanded', false);
    });

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

    const modal = document.createElement('div');
    modal.id = 'modal';
    modal.role = 'dialog';
    modal.setAttribute('aria-modal', 'true');
    modal.tabIndex = -1;
    modal.style.cssText = 'display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.5);align-items:center;justify-content:center;z-index:2000;';
    modal.innerHTML = `
      <div id="modal-content" style="max-width:600px;background:#fff;border-radius:12px;padding:1.5rem 2rem;color:#222;overflow-y:auto;max-height:80vh;position:relative;">
        <button id="modal-close" aria-label="Close dialog" style="position:absolute;top:12px;right:16px;background:none;border:none;font-size:1.5rem;cursor:pointer;color:inherit;">&times;</button>
        <h2 id="modal-title"></h2>
        <div id="modal-body"></div>
      </div>
    `;
    document.body.appendChild(modal);

    const modalTitle = modal.querySelector('#modal-title');
    const modalBody = modal.querySelector('#modal-body');
    const modalCloseBtn = modal.querySelector('#modal-close');

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
        title: 'Terms &amp; Conditions',
        content: `<p>By using PAPERPREP, you agree to our terms and conditions. We provide our tools &quot;as is&quot; without warranties. Use the services responsibly and respect intellectual property rights.</p>`
      }
    };

    document.querySelectorAll('.info-menu-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        const key = btn.getAttribute('data-info');
        if (infoContents[key]) {
          modalTitle.innerHTML = infoContents[key].title;
          modalBody.innerHTML = infoContents[key].content;
          modal.style.display = 'flex';
          modal.focus();
          dropdownMenu.classList.remove('open');
          dropdownButton.setAttribute('aria-expanded', false);
        }
      });
    });

    modalCloseBtn.addEventListener('click', () => { modal.style.display = 'none'; });
    document.addEventListener('keydown', e => {
      if(e.key === 'Escape' && modal.style.display === 'flex') {
        modal.style.display = 'none';
      }
    });
  </script>
</body>
</html>
"""

TOOL_PAGES = {
    "pdf-to-word": {"title": "PDF to Word", "description": "Convert your PDF documents to editable Word files.", "accept": ".pdf", "multiple": False, "endpoint": "/convert/pdf-to-word"},
    "jpg-to-word": {"title": "JPG to Word", "description": "Extract text from your JPG images into Word format.", "accept": "image/jpeg,image/png,image/bmp,image/gif,image/tiff", "multiple": False, "endpoint": "/convert/jpg-to-word"},
    "ppt-to-pdf": {"title": "PPT to PDF", "description": "Easily convert your PowerPoint presentations to PDF files.", "accept": ".ppt,.pptx", "multiple": False, "endpoint": "/convert/ppt-to-pdf"},
    "pdf-to-ppt": {"title": "PDF to PPT", "description": "Convert PDF documents back to editable PowerPoint presentations.", "accept": ".pdf", "multiple": False, "endpoint": "/convert/pdf-to-ppt"},
    "multiple-images-to-pdf": {"title": "Multiple Images into One PDF", "description": "Combine multiple images into a single PDF file easily.", "accept": "image/jpeg,image/png,image/bmp,image/gif,image/tiff", "multiple": True, "endpoint": "/convert/multiple-images-to-pdf"},
    "merge-pdf": {"title": "Merge PDF", "description": "Combine multiple PDF files into one seamless document.", "accept": ".pdf", "multiple": True, "endpoint": "/convert/merge-pdf"},
    "image-compressor": {"title": "Image Compressor", "description": "Compress images to reduce file size without losing quality.", "accept": "image/jpeg,image/png,image/bmp,image/gif,image/tiff", "multiple": False, "endpoint": "/convert/image-compressor"},
    "pdf-compressor": {"title": "PDF Compressor", "description": "Reduce the size of your PDF files for faster sharing.", "accept": ".pdf", "multiple": False, "endpoint": "/convert/pdf-compressor"},
}

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/tool/<tool>')
def tool_page(tool):
    tooldata = TOOL_PAGES.get(tool)
    if not tooldata:
        abort(404)
    return render_template_string(TOOL_PAGE_HTML_TEMPLATE, **tooldata)

@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(app.static_folder, 'favicon.ico'))

@app.route('/convert/pdf-to-word', methods=['POST'])
def pdf_to_word():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if not file or not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        return "Invalid file", 400
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        file.save(tmp_pdf.name)
        tmp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        tmp_docx.close()
        try:
            cv = Converter(tmp_pdf.name)
            cv.convert(tmp_docx.name)
            cv.close()
            os.unlink(tmp_pdf.name)
            return send_file(tmp_docx.name, as_attachment=True, download_name="converted.docx")
        except Exception as e:
            os.unlink(tmp_pdf.name)
            os.unlink(tmp_docx.name)
            return f"Conversion error: {str(e)}", 500

@app.route('/convert/jpg-to-word', methods=['POST'])
def jpg_to_word():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if not file or not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return "Invalid file", 400
    try:
        img = Image.open(file.stream)
        text = pytesseract.image_to_string(img)
    except Exception as e:
        return f"OCR failed: {str(e)}", 500
    from docx import Document
    doc = Document()
    doc.add_paragraph(text)
    tmp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp_docx.name)
    return send_file(tmp_docx.name, as_attachment=True, download_name="converted.docx")

@app.route('/convert/ppt-to-pdf', methods=['POST'])
def ppt_to_pdf():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if not file or not allowed_file(file.filename, ALLOWED_PPT_EXTENSIONS):
        return "Invalid file", 400
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as tmp_ppt:
        file.save(tmp_ppt.name)
        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        try:
            prs = Presentation(tmp_ppt.name)
            c = canvas.Canvas(tmp_pdf.name, pagesize=letter)
            width, height = letter
            for _ in prs.slides:
                c.setFont("Helvetica-Bold", 24)
                c.drawCentredString(width / 2, height / 2, "Slide Preview Not Available")
                c.showPage()
            c.save()
            os.unlink(tmp_ppt.name)
            return send_file(tmp_pdf.name, as_attachment=True, download_name="converted.pdf")
        except Exception as e:
            os.unlink(tmp_ppt.name)
            os.unlink(tmp_pdf.name)
            return f"Conversion error: {str(e)}", 500

@app.route('/convert/pdf-to-ppt', methods=['POST'])
def pdf_to_ppt():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if not file or not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        return "Invalid file", 400
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        file.save(tmp_pdf.name)
        tmp_pptx = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
        try:
            reader = PdfReader(tmp_pdf.name)
            prs = Presentation()
            blank_slide_layout = prs.slide_layouts[6]
            for _ in reader.pages:
                prs.slides.add_slide(blank_slide_layout)
            prs.save(tmp_pptx.name)
            os.unlink(tmp_pdf.name)
            return send_file(tmp_pptx.name, as_attachment=True, download_name="converted.pptx")
        except Exception as e:
            os.unlink(tmp_pdf.name)
            os.unlink(tmp_pptx.name)
            return f"Conversion error: {str(e)}", 500

@app.route('/convert/multiple-images-to-pdf', methods=['POST'])
def multiple_images_to_pdf():
    files = request.files.getlist("files")
    if not files or not any(allowed_file(f.filename, ALLOWED_IMAGE_EXTENSIONS) for f in files):
        return "Invalid files", 400
    images = []
    for file in files:
        try:
            img = Image.open(file.stream).convert("RGB")
            images.append(img)
        except:
            return f"Failed to process file {file.filename}", 400
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        images[0].save(tmp_pdf.name, save_all=True, append_images=images[1:])
        return send_file(tmp_pdf.name, as_attachment=True, download_name="combined.pdf")
    except Exception as e:
        os.unlink(tmp_pdf.name)
        return f"Conversion error: {str(e)}", 500

@app.route('/convert/merge-pdf', methods=['POST'])
def merge_pdf():
    files = request.files.getlist("files")
    if not files or not any(allowed_file(f.filename, ALLOWED_PDF_EXTENSIONS) for f in files):
        return "Invalid files", 400
    merger = PdfMerger()
    try:
        for file in files:
            if allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                file.save(tmp.name)
                merger.append(tmp.name)
                os.unlink(tmp.name)
        output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        merger.write(output.name)
        merger.close()
        return send_file(output.name, as_attachment=True, download_name="merged.pdf")
    except Exception as e:
        return f"Merging error: {str(e)}", 500

@app.route('/convert/image-compressor', methods=['POST'])
def image_compressor():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if not file or not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return "Invalid file", 400
    try:
        img = Image.open(file.stream)
        tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        img.save(tmp_img.name, optimize=True, quality=50)
        return send_file(tmp_img.name, as_attachment=True, download_name="compressed.jpg")
    except Exception as e:
        return f"Compression error: {str(e)}", 500

@app.route('/convert/pdf-compressor', methods=['POST'])
def pdf_compressor():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if not file or not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        return "Invalid file", 400
    tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    file.save(tmp_in.name)
    try:
        reader = PdfReader(tmp_in.name)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(tmp_out.name, "wb") as f_out:
            writer.write(f_out)
        os.unlink(tmp_in.name)
        return send_file(tmp_out.name, as_attachment=True, download_name="compressed.pdf")
    except Exception as e:
        os.unlink(tmp_in.name)
        if os.path.exists(tmp_out.name):
            os.unlink(tmp_out.name)
        return f"Compression error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
