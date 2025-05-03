from flask import Flask, render_template_string

app = Flask(__name__)

# Shared CSS for all pages
base_css = """
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&family=Inter:wght@400;600&display=swap');

  :root {
    --color-bg-light: #ffffff;
    --color-bg-dark: #1a1a2e;
    --color-primary: #3b82f6;
    --color-primary-dark: #60a5fa;
    --color-text-light: #1f2937;
    --color-text-dark: #d1d5db;
    --color-card-bg-light: #f9fafb;
    --color-card-bg-dark: #16213e;
    --color-btn-bg-light: #3b82f6;
    --color-btn-bg-dark: #2563eb;
    --color-btn-text-light: #ffffff;
    --color-btn-text-dark: #e0e7ff;
    --color-border-light: #e5e7eb;
    --color-border-dark: #0f172a;
    --shadow-light: 0 8px 16px rgba(59, 130, 246, 0.15);
    --shadow-dark: 0 8px 16px rgba(37, 99, 235, 0.4);
  }

  body {
    margin: 0;
    font-family: 'Inter', sans-serif;
    background-color: var(--color-bg-light);
    color: var(--color-text-light);
    overflow-x: hidden;
  }
  body.dark-theme {
    background-color: var(--color-bg-dark);
    color: var(--color-text-dark);
  }

  nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 56px;
    background: var(--color-card-bg-light);
    border-bottom: 1px solid var(--color-border-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1rem;
    z-index: 1001;
    box-shadow: var(--shadow-light);
    user-select: none;
  }
  body.dark-theme nav {
    background: var(--color-card-bg-dark);
    border-color: var(--color-border-dark);
    box-shadow: var(--shadow-dark);
  }

  nav .logo {
    font-family: 'Orbitron', sans-serif;
    font-weight: 600;
    font-size: 1.5rem;
    color: var(--color-primary);
  }
  body.dark-theme nav .logo {
    color: var(--color-primary-dark);
  }

  /* Menu button container */
  .menu-container {
    position: relative;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  /* Dropdown Menu button */
  .menu-button {
    position: relative;
    background: none;
    border: none;
    cursor: pointer;
    font-family: 'Orbitron', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    color: var(--color-primary);
    padding: 6px 12px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    user-select: none;
    transition: background-color 0.3s ease, color 0.3s ease;
  }
  .menu-button svg {
    width: 20px;
    height: 20px;
    margin-left: 6px;
    fill: currentColor;
    transition: transform 0.3s ease;
  }
  .menu-button[aria-expanded="true"] svg {
    transform: rotate(180deg);
  }
  .menu-button:hover, .menu-button:focus {
    background-color: var(--color-primary);
    color: #fff;
    outline: none;
  }
  body.dark-theme .menu-button {
    color: var(--color-primary-dark);
  }
  body.dark-theme .menu-button:hover,
  body.dark-theme .menu-button:focus {
    background-color: var(--color-primary-dark);
    color: #fff;
    outline: none;
  }

  /* Dropdown menu */
  .dropdown-menu {
    position: absolute;
    top: 42px;
    right: 0;
    background: var(--color-card-bg-light);
    border: 1px solid var(--color-border-light);
    border-radius: 8px;
    box-shadow: var(--shadow-light);
    display: none;
    min-width: 200px;
    z-index: 1002;
    user-select: none;
  }
  body.dark-theme .dropdown-menu {
    background: var(--color-card-bg-dark);
    border-color: var(--color-border-dark);
    box-shadow: var(--shadow-dark);
  }
  .dropdown-menu.open {
    display: block;
  }
  .dropdown-menu ul {
    list-style: none;
    margin: 0; padding: 8px 0;
    border-radius: 8px;
  }
  .dropdown-menu ul li {
    margin: 0;
  }
  .dropdown-menu ul li a {
    display: block;
    padding: 10px 16px;
    color: var(--color-primary);
    text-decoration: none;
    font-weight: 600;
    font-size: 1rem;
    transition: background-color 0.2s ease;
  }
  .dropdown-menu ul li a:hover,
  .dropdown-menu ul li a:focus {
    background-color: var(--color-primary);
    color: #fff;
    outline: none;
  }
  body.dark-theme .dropdown-menu ul li a {
    color: var(--color-primary-dark);
  }
  body.dark-theme .dropdown-menu ul li a:hover,
  body.dark-theme .dropdown-menu ul li a:focus {
    background-color: var(--color-primary-dark);
    color: #fff;
    outline: none;
  }

  /* Theme toggle button */
  #theme-toggle {
    background-color: var(--color-btn-bg-light);
    color: var(--color-btn-text-light);
    font-family: 'Orbitron', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    border: none;
    border-radius: 25px;
    padding: 6px 14px;
    cursor: pointer;
    box-shadow: var(--shadow-light);
    transition: background-color 0.3s ease;
    user-select: none;
  }
  #theme-toggle:hover, #theme-toggle:focus {
    background-color: var(--color-primary-dark);
    outline: none;
  }
  body.dark-theme #theme-toggle {
    background-color: var(--color-btn-bg-dark);
    color: var(--color-btn-text-dark);
    box-shadow: var(--shadow-dark);
  }
  body.dark-theme #theme-toggle:hover,
  body.dark-theme #theme-toggle:focus {
    background-color: var(--color-primary);
    outline: none;
  }

  main {
    margin-top: 56px;
    padding: 1rem;
    max-width: 360px;
    margin-left: auto;
    margin-right: auto;
    user-select: none;
  }

  h2 {
    font-family: 'Orbitron', sans-serif;
    color: var(--color-primary);
    text-align: center;
    margin-bottom: 1.5rem;
  }
  body.dark-theme h2 {
    color: var(--color-primary-dark);
  }

  .tool-container {
    background: var(--color-card-bg-light);
    border-radius: 15px;
    padding: 2rem 1.5rem;
    box-shadow: var(--shadow-light);
    text-align: center;
  }
  body.dark-theme .tool-container {
    background: var(--color-card-bg-dark);
    box-shadow: var(--shadow-dark);
  }

  .tool-icon-large {
    width: 96px;
    height: 96px;
    margin-bottom: 1rem;
    fill: var(--color-primary);
    transition: fill 0.3s ease;
  }
  body.dark-theme .tool-icon-large {
    fill: var(--color-primary-dark);
  }

  label.file-label {
    padding: 12px 24px;
    border-radius: 30px;
    background-color: var(--color-btn-bg-light);
    color: var(--color-btn-text-light);
    cursor: pointer;
    font-weight: 700;
    box-shadow: var(--shadow-light);
    margin-bottom: 12px;
    display: inline-block;
    transition: background-color 0.3s ease;
    user-select: none;
    font-size: 1rem;
  }
  label.file-label:hover, label.file-label:focus {
    background-color: var(--color-primary-dark);
    outline: none;
  }
  body.dark-theme label.file-label {
    background-color: var(--color-btn-bg-dark);
    color: var(--color-btn-text-dark);
    box-shadow: var(--shadow-dark);
  }
  body.dark-theme label.file-label:hover, body.dark-theme label.file-label:focus {
    background-color: var(--color-btn-bg-light);
    color: var(--color-btn-text-light);
    outline: none;
  }

  input[type="file"] {
    display: none;
  }

  button.submit-btn {
    margin-top: 12px;
    padding: 12px 0;
    width: 100%;
    border: none;
    border-radius: 30px;
    background-color: var(--color-btn-bg-light);
    color: var(--color-btn-text-light);
    font-weight: 700;
    font-size: 1.1rem;
    cursor: pointer;
    box-shadow: var(--shadow-light);
    transition: background-color 0.3s ease;
    user-select: none;
  }
  button.submit-btn:hover, button.submit-btn:focus {
    background-color: var(--color-primary-dark);
    outline: none;
  }
  body.dark-theme button.submit-btn {
    background-color: var(--color-btn-bg-dark);
    color: var(--color-btn-text-dark);
    box-shadow: var(--shadow-dark);
  }
  body.dark-theme button.submit-btn:hover, body.dark-theme button.submit-btn:focus {
    background-color: var(--color-btn-bg-light);
    color: var(--color-btn-text-light);
    outline: none;
  }

  section.info-section {
    margin-top: 1rem;
    background: var(--color-card-bg-light);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: var(--shadow-light);
    user-select: text;
  }
  body.dark-theme section.info-section {
    background: var(--color-card-bg-dark);
    box-shadow: var(--shadow-dark);
  }
  section.info-section h2 {
    font-family: 'Orbitron', sans-serif;
    margin-bottom: 0.75rem;
    color: var(--color-primary);
  }
  body.dark-theme section.info-section h2 {
    color: var(--color-primary-dark);
  }
  section.info-section p, section.info-section a {
    font-weight: 400;
    font-size: 0.95rem;
    line-height: 1.5;
  }
  section.info-section a {
    color: var(--color-primary);
    text-decoration: underline;
  }
  body.dark-theme section.info-section a {
    color: var(--color-primary-dark);
  }

  footer {
    text-align: center;
    margin: 2rem 0 1rem;
    font-size: 0.75rem;
    color: var(--color-text-light);
    user-select:none;
  }
  body.dark-theme footer {
    color: var(--color-text-dark);
  }

  a:focus, button:focus, label.file-label:focus, .tool-container:focus-within, .menu-button:focus {
    outline: 3px solid var(--color-primary);
    outline-offset: 2px;
  }

  [id] {
    scroll-margin-top: 70px;
  }
"""

base_js = """
  const menuButton = document.getElementById('menu-button');
  const dropdownMenu = document.getElementById('dropdown-menu');

  function closeDropdown() {
    dropdownMenu.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
  }
  function openDropdown() {
    dropdownMenu.classList.add('open');
    menuButton.setAttribute('aria-expanded', 'true');
  }

  menuButton.addEventListener('click', () => {
    const isOpen = dropdownMenu.classList.contains('open');
    if(isOpen){
      closeDropdown();
    } else {
      openDropdown();
    }
  });

  document.addEventListener('click', (e) => {
    if(!menuButton.contains(e.target) && !dropdownMenu.contains(e.target)){
      closeDropdown();
    }
  });

  menuButton.addEventListener('keydown', e => {
    if(e.key === 'ArrowDown' || e.key === 'Enter' || e.key === ' '){
      e.preventDefault();
      openDropdown();
      dropdownMenu.querySelector('a').focus();
    }
    if(e.key === 'Escape'){
      closeDropdown();
      menuButton.focus();
    }
  });

  dropdownMenu.addEventListener('keydown', e => {
    if(e.key === 'Escape'){
      closeDropdown();
      menuButton.focus();
    }
  });

  const themeToggleBtn = document.getElementById('theme-toggle');
  const storedTheme = localStorage.getItem('paperprep-theme');
  function applyTheme(theme) {
    if(theme === 'dark') {
      document.body.classList.add('dark-theme');
      themeToggleBtn.textContent = 'Light Mode';
    } else {
      document.body.classList.remove('dark-theme');
      themeToggleBtn.textContent = 'Dark Mode';
    }
    localStorage.setItem('paperprep-theme', theme);
  }
  applyTheme(storedTheme || 'light');

  themeToggleBtn.addEventListener('click', () => {
    if(document.body.classList.contains('dark-theme')) {
      applyTheme('light');
    } else {
      applyTheme('dark');
    }
  });

  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
          e.preventDefault();
          const target = document.querySelector(this.getAttribute('href'));
          if(target){
            target.scrollIntoView({behavior: 'smooth', block: 'start'});
            target.focus();
          }
      });
  });
"""

def render_base_page(title, description, keywords, content_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
<title>{title} - PAPERPREP</title>
<meta name="description" content="{description}" />
<meta name="keywords" content="{keywords}" />
<meta name="author" content="PAPERPREP Team" />
<link rel="icon" type="image/x-icon" href="{{{{ url_for('static', filename='fevicon.ico') }}}}" />
<style>
{base_css}
</style>
</head>
<body>
<nav role="navigation" aria-label="Primary navigation">
  <div class="logo" tabindex="0">PAPERPREP</div>
  <div class="menu-container">
    <button class="menu-button" id="menu-button" aria-haspopup="true" aria-expanded="false" aria-controls="dropdown-menu" aria-label="Open menu">
      Menu
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path d="M7 10l5 5 5-5H7z"/>
      </svg>
    </button>
    <button id="theme-toggle" aria-label="Toggle dark mode">Dark Mode</button>
  </div>

  <div class="dropdown-menu" id="dropdown-menu" role="menu" aria-label="Site menu">
    <ul>
      <li><a href="/" role="menuitem" tabindex="-1">Home</a></li>
      <li><a href="/pdf-to-word" role="menuitem" tabindex="-1">PDF to Word</a></li>
      <li><a href="/jpg-to-word" role="menuitem" tabindex="-1">JPG to Word</a></li>
      <li><a href="/ppt-to-pdf" role="menuitem" tabindex="-1">PPT to PDF</a></li>
      <li><a href="/pdf-to-ppt" role="menuitem" tabindex="-1">PDF to PPT</a></li>
      <li><a href="/images-to-pdf" role="menuitem" tabindex="-1">Images to PDF</a></li>
      <li><a href="/merge-pdf" role="menuitem" tabindex="-1">Merge PDFs</a></li>
      <li><a href="/image-compressor" role="menuitem" tabindex="-1">Image Compressor</a></li>
      <li><a href="/pdf-compressor" role="menuitem" tabindex="-1">PDF Compressor</a></li>
      <li><a href="#about-section" role="menuitem" tabindex="-1">About</a></li>
      <li><a href="#privacy-section" role="menuitem" tabindex="-1">Privacy</a></li>
      <li><a href="#contact-section" role="menuitem" tabindex="-1">Contact</a></li>
      <li><a href="#terms-section" role="menuitem" tabindex="-1">Terms &amp; Conditions</a></li>
    </ul>
  </div>
</nav>

<main tabindex="0">
  {content_html}
</main>

<footer>
  © 2024 PAPERPREP - Made with 💡 for college projects
</footer>
<script>
{base_js}
</script>
</body>
</html>"""

home_content = """
<h2>Welcome to PAPERPREP</h2>
<section class="info-section" id="about-section" tabindex="0">
  <h2>About PAPERPREP</h2>
  <p>PAPERPREP is your all-in-one platform for document and image conversion needs. Transform your files effortlessly with support for various formats, prepared for college projects and professional showcase, featuring a clean, futuristic, and user-friendly interface with responsive design for all devices.</p>
</section>
<section class="info-section" id="privacy-section" tabindex="0">
  <h2>Privacy Policy</h2>
  <p>Your privacy matters. PAPERPREP does not store or share your files. All conversions happen locally or are securely processed. We recommend reviewing the specific policies before uploading sensitive documents.</p>
</section>
<section class="info-section" id="contact-section" tabindex="0">
  <h2>Contact Us</h2>
  <p>For feedback, suggestions, or support, reach out to us at <a href="mailto:support@paperprep.example.com">support@paperprep.example.com</a>. We are here to help you get the best experience.</p>
</section>
<section class="info-section" id="terms-section" tabindex="0">
  <h2>Terms &amp; Conditions</h2>
  <p>By using PAPERPREP, you agree to our terms and conditions. Use the platform responsibly. We disclaim liability for data loss or inaccurate conversions. Please backup your files before use.</p>
</section>
"""

def render_tool_page(title, description, keywords, svg_icon, file_accept, label_text, action_alert_text):
    content = f"""
    <h2>{title}</h2>
    <div class="tool-container">
      {svg_icon}
      <form onsubmit="alert('{action_alert_text}'); return false;">
        <label class="file-label" for="file-input">{label_text}</label>
        <input type="file" id="file-input" accept="{file_accept}" />
        <button type="submit" class="submit-btn">Convert</button>
      </form>
    </div>
    """
    return render_base_page(title, description, keywords, content)

svg_pdf_to_word = """
<svg class="tool-icon-large" viewBox="0 0 64 64" aria-hidden="true" focusable="false" >
  <rect x="12" y="10" width="40" height="44" rx="6" ry="6" stroke="currentColor" fill="none" stroke-width="3"/>
  <path fill="currentColor" fill-opacity="0.15" d="M20 18h24v12H20z"/>
  <path stroke="currentColor" stroke-width="2" d="M24 30h16M24 36h16" fill="none" />
  <text x="32" y="50" font-family="Orbitron" font-size="12" fill="currentColor" text-anchor="middle" dominant-baseline="middle" opacity="0.7">PDF→DOC</text>
</svg>
"""

svg_jpg_to_word = """
<svg class="tool-icon-large" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
  <rect x="10" y="10" width="44" height="44" rx="8" ry="8" stroke="currentColor" fill="none" stroke-width="3"/>
  <circle cx="32" cy="30" r="12" fill="currentColor" fill-opacity="0.12"/>
  <path stroke="currentColor" stroke-width="2" d="M14 46h36" fill="none" stroke-linecap="round"/>
  <text x="32" y="54" font-family="Orbitron" font-size="12" fill="currentColor" text-anchor="middle" dominant-baseline="middle" opacity="0.7">JPG→DOC</text>
</svg>
"""

svg_ppt_to_pdf = """
<svg class="tool-icon-large" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
  <rect x="14" y="14" width="36" height="36" rx="6" ry="6" stroke="currentColor" fill="none" stroke-width="3"/>
  <path fill="currentColor" fill-opacity="0.15" d="M22 24h20v16H22z"/>
  <text x="32" y="50" font-family="Orbitron" font-size="12" fill="currentColor" text-anchor="middle" dominant-baseline="middle" opacity="0.7">PPT→PDF</text>
</svg>
"""

svg_pdf_to_ppt = """
<svg class="tool-icon-large" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
  <rect x="14" y="14" width="36" height="36" rx="6" ry="6" stroke="currentColor" fill="none" stroke-width="3"/>
  <path fill="currentColor" fill-opacity="0.15" d="M22 24h20v16H22z"/>
  <line x1="22" y1="44" x2="42" y2="44" stroke="currentColor" stroke-width="2" />
  <text x="32" y="50" font-family="Orbitron" font-size="12" fill="currentColor" text-anchor="middle" dominant-baseline="middle" opacity="0.7">PDF→PPT</text>
</svg>
"""

svg_images_to_pdf = """
<svg class="tool-icon-large" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
  <rect x="8" y="14" width="48" height="36" rx="6" ry="6" stroke="currentColor" fill="none" stroke-width="3"/>
  <circle cx="24" cy="32" r="12" fill="currentColor" fill-opacity="0.12"/>
  <rect x="38" y="32" width="14" height="10" fill="currentColor" fill-opacity="0.12" rx="2" ry="2"/>
  <text x="32" y="52" font-family="Orbitron" font-size="10" fill="currentColor" text-anchor="middle" dominant-baseline="middle" opacity="0.7">Imgs→PDF</text>
</svg>
"""

svg_merge_pdf = """
<svg class="tool-icon-large" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
  <rect x="10" y="14" width="44" height="36" rx="6" ry="6" stroke="currentColor" fill="none" stroke-width="3"/>
  <rect x="16" y="22" width="32" height="12" fill="currentColor" fill-opacity="0.15"/>
  <rect x="16" y="38" width="32" height="12" fill="currentColor" fill-opacity="0.15"/>
  <text x="32" y="52" font-family="Orbitron" font-size="10" fill="currentColor" text-anchor="middle" dominant-baseline="middle" opacity="0.7">Merge PDF</text>
</svg>
"""

svg_image_compressor = """
<svg class="tool-icon-large" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
  <circle cx="32" cy="32" r="26" stroke="currentColor" fill="none" stroke-width="3"/>
  <line x1="32" y1="10" x2="32" y2="54" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <polygon points="22,38 32,48 42,38" fill="currentColor" fill-opacity="0.3"/>
  <text x="32" y="56" font-family="Orbitron" font-size="10" fill="currentColor" text-anchor="middle" dominant-baseline="middle" opacity="0.7">Img Compress</text>
</svg>
"""

svg_pdf_compressor = """
<svg class="tool-icon-large" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
  <rect x="14" y="14" width="36" height="36" rx="6" ry="6" stroke="currentColor" fill="none" stroke-width="3"/>
  <path d="M22 30h20v8H22z" fill="currentColor" fill-opacity="0.15"/>
  <text x="32" y="52" font-family="Orbitron" font-size="10" fill="currentColor" text-anchor="middle" dominant-baseline="middle" opacity="0.7">PDF Compress</text>
</svg>
"""

@app.route("/")
def home():
    return render_template_string(render_base_page(
        "Home",
        "Welcome to PAPERPREP document and image conversion platform. Convert PDF, Word, JPG, PPT and compress your files with a futuristic and easy-to-use interface.",
        "document conversion, pdf to word, jpg to word, ppt to pdf, pdf to ppt, merge pdf, image compressor, pdf compressor",
        home_content
    ))

@app.route("/pdf-to-word")
def pdf_to_word():
    return render_template_string(render_tool_page(
        "PDF to Word",
        "Convert your PDF documents to editable Word files quickly and easily.",
        "pdf to word, convert pdf to doc, pdf converter",
        svg_pdf_to_word,
        ".pdf",
        "Choose PDF file",
        "PDF to Word conversion feature not implemented."
    ))

@app.route("/jpg-to-word")
def jpg_to_word():
    return render_template_string(render_tool_page(
        "JPG to Word",
        "Extract text from JPG or PNG image files and save as Word documents.",
        "jpg to word, image to doc, jpg converter",
        svg_jpg_to_word,
        "image/jpeg,image/png",
        "Choose JPG or PNG file",
        "JPG to Word conversion feature not implemented."
    ))

@app.route("/ppt-to-pdf")
def ppt_to_pdf():
    return render_template_string(render_tool_page(
        "PPT to PDF",
        "Convert your PowerPoint presentations to PDF format for easy sharing.",
        "ppt to pdf, powerpoint to pdf, presentation converter",
        svg_ppt_to_pdf,
        ".ppt,.pptx",
        "Choose PPT file",
        "PPT to PDF conversion feature not implemented."
    ))

@app.route("/pdf-to-ppt")
def pdf_to_ppt():
    return render_template_string(render_tool_page(
        "PDF to PPT",
        "Convert PDF files back to editable PowerPoint presentations.",
        "pdf to ppt, convert pdf to powerpoint, pdf presentation converter",
        svg_pdf_to_ppt,
        ".pdf",
        "Choose PDF file",
        "PDF to PPT conversion feature not implemented."
    ))

@app.route("/images-to-pdf")
def images_to_pdf():
    return render_template_string(render_tool_page(
        "Images to PDF",
        "Combine multiple images into a single PDF document easily.",
        "images to pdf, picture to pdf, jpg to pdf, png to pdf",
        svg_images_to_pdf,
        "image/*",
        "Choose image files",
        "Multiple Images to one PDF feature not implemented."
    ))

@app.route("/merge-pdf")
def merge_pdf():
    return render_template_string(render_tool_page(
        "Merge PDFs",
        "Merge multiple PDF files into one seamless document.",
        "merge pdf, combine pdf, pdf joiner",
        svg_merge_pdf,
        ".pdf",
        "Choose PDF files",
        "Merge PDF feature not implemented."
    ))

@app.route("/image-compressor")
def image_compressor():
    return render_template_string(render_tool_page(
        "Image Compressor",
        "Compress image files to reduce their size without losing quality.",
        "image compressor, compress jpg, reduce image size",
        svg_image_compressor,
        "image/*",
        "Choose image file",
        "Image compressor feature not implemented."
    ))

@app.route("/pdf-compressor")
def pdf_compressor():
    return render_template_string(render_tool_page(
        "PDF Compressor",
        "Reduce the file size of PDF documents for easier sharing.",
        "pdf compressor, reduce pdf size",
        svg_pdf_compressor,
        ".pdf",
        "Choose PDF file",
        "PDF compressor feature not implemented."
    ))

if __name__ == "__main__":
    app.run(debug=True , port = 5000 , host= 0.0.0.0 )
