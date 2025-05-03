from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__, static_folder='static')

# Load full HTML page from embedded string
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

    .btn-action {
      background-color: var(--color-button-bg);
      color: var(--color-button-text);
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 25px;
      font-weight: 600;
      cursor: pointer;
      user-select: none;
      transition: background-color 0.3s;
    }
    .btn-action:hover,
    .btn-action:focus {
      background-color: var(--color-button-hover-bg);
      outline: none;
    }
    body.dark .btn-action {
      background-color: var(--color-primary-light);
      color: var(--color-text-dark);
    }
    body.dark .btn-action:hover,
    body.dark .btn-action:focus {
      background-color: var(--color-primary);
      color: #fff;
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

    /* CONTACT / ABOUT / ETC SECTIONS */
    section.info-section {
      background-color: #fff;
      padding: 1rem 1.5rem;
      border-radius: 12px;
      box-shadow: 0 1px 8px rgb(0 0 0 / 0.1);
      max-width: 800px;
      margin: 0 auto;
      margin-top: 1rem;
      color: var(--color-text-light);
    }
    body.dark section.info-section {
      background-color: #222;
      color: var(--color-text-dark);
      box-shadow: 0 1px 8px rgba(255 255 255 / 0.1);
    }
    section.info-section h2 {
      margin-top: 0;
      margin-bottom: 0.5rem;
    }
    section.info-section p {
      line-height: 1.4;
      margin-bottom: 0.5rem;
    }

    /* Responsive text scaling */
    @media (max-width: 400px) {
      .card-title {
        font-size: 1.1rem;
      }
      .card-desc {
        font-size: 0.8rem;
      }
      .btn-action {
        font-size: 0.9rem;
      }
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
        <li><a href="#about" role="menuitem" tabindex="0">About</a></li>
        <li><a href="#privacy" role="menuitem" tabindex="0">Privacy</a></li>
        <li><a href="#contact" role="menuitem" tabindex="0">Contact</a></li>
        <li><a href="#terms" role="menuitem" tabindex="0">Terms & Conditions</a></li>
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
        <!-- Tool Card Template -->
        <article class="card" role="listitem" tabindex="0">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64" >
            <path d="M48 2H16C12.7 2 10 4.7 10 8V56C10 59.3 12.7 62 16 62H48C51.3 62 54 59.3 54 56V8C54 4.7 51.3 2 48 2Z" />
            <path d="M28 18H36V46H28Z" fill="#f4a261"/>
            <path d="M36 24L44 18" stroke="#5c6ac4" stroke-width="2"/>
          </svg>
          <h3 class="card-title">PDF to Word</h3>
          <p class="card-desc">Convert your PDF documents to editable Word files.</p>
          <button class="btn-action" onclick="alert('PDF to Word tool coming soon!');">Try Now</button>
        </article>

        <article class="card" role="listitem" tabindex="0">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64" >
            <circle cx="32" cy="32" r="30" fill="#8c97f9" />
            <rect x="15" y="22" width="34" height="20" rx="4" ry="4" fill="#61a5c2"/>
            <circle cx="32" cy="32" r="8" fill="#f4a261"/>
          </svg>
          <h3 class="card-title">JPG to Word</h3>
          <p class="card-desc">Extract text from your JPG images into Word format.</p>
          <button class="btn-action" onclick="alert('JPG to Word tool coming soon!');">Try Now</button>
        </article>

        <article class="card" role="listitem" tabindex="0">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <rect x="14" y="10" width="36" height="44" rx="6" ry="6" fill="#5c6ac4"/>
            <rect x="20" y="18" width="24" height="28" fill="#f4a261"/>
            <rect x="20" y="22" width="24" height="6" fill="#fff"/>
            <rect x="20" y="34" width="24" height="6" fill="#fff"/>
          </svg>
          <h3 class="card-title">PPT to PDF</h3>
          <p class="card-desc">Easily convert your PowerPoint presentations to PDF files.</p>
          <button class="btn-action" onclick="alert('PPT to PDF tool coming soon!');">Try Now</button>
        </article>

        <article class="card" role="listitem" tabindex="0">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <path d="M10 54L54 10" stroke="#5c6ac4" stroke-width="5" stroke-linecap="round"/>
            <circle cx="22" cy="22" r="10" fill="#f4a261" />
            <circle cx="42" cy="42" r="10" fill="#61a5c2" />
            <text x="22" y="26" font-size="10" text-anchor="middle" fill="#fff" font-family="Segoe UI">PPT</text>
            <text x="42" y="46" font-size="10" text-anchor="middle" fill="#fff" font-family="Segoe UI">PDF</text>
          </svg>
          <h3 class="card-title">PDF to PPT</h3>
          <p class="card-desc">Convert PDF documents back to editable PowerPoint presentations.</p>
          <button class="btn-action" onclick="alert('PDF to PPT tool coming soon!');">Try Now</button>
        </article>

        <article class="card" role="listitem" tabindex="0">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <rect x="8" y="12" width="20" height="40" rx="4" ry="4" fill="#5c6ac4"/>
            <rect x="36" y="12" width="20" height="40" rx="4" ry="4" fill="#61a5c2"/>
            <path d="M16 26H44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
            <path d="M16 38H44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <h3 class="card-title">Multiple Images into One PDF</h3>
          <p class="card-desc">Combine multiple images into a single PDF file easily.</p>
          <button class="btn-action" onclick="alert('Multiple Images to PDF tool coming soon!');">Try Now</button>
        </article>

        <article class="card" role="listitem" tabindex="0">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <rect x="12" y="14" width="40" height="36" rx="6" ry="6" fill="#5c6ac4"/>
            <path d="M16 20L48 44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
            <path d="M48 20L16 44" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <h3 class="card-title">Merge PDF</h3>
          <p class="card-desc">Combine multiple PDF files into one seamless document.</p>
          <button class="btn-action" onclick="alert('Merge PDF tool coming soon!');">Try Now</button>
        </article>

        <article class="card" role="listitem" tabindex="0">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="26" stroke="#5c6ac4" stroke-width="4" fill="#61a5c2"/>
            <path d="M20 32H44" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
            <path d="M32 20V44" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <h3 class="card-title">Image Compressor</h3>
          <p class="card-desc">Compress images to reduce file size without losing quality.</p>
          <button class="btn-action" onclick="alert('Image compressor coming soon!');">Try Now</button>
        </article>

        <article class="card" role="listitem" tabindex="0">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <rect x="14" y="18" width="36" height="28" rx="6" ry="6" fill="#5c6ac4"/>
            <path d="M22 26H42" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
            <path d="M22 38H42" stroke="#f4a261" stroke-width="4" stroke-linecap="round"/>
          </svg>
          <h3 class="card-title">PDF Compressor</h3>
          <p class="card-desc">Reduce the size of your PDF files for faster sharing.</p>
          <button class="btn-action" onclick="alert('PDF compressor coming soon!');">Try Now</button>
        </article>

        <article class="card" role="listitem" tabindex="0">
          <svg class="card-icon" aria-hidden="true" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="30" stroke="#5c6ac4" stroke-width="4" fill="#f4a261"/>
            <text x="32" y="38" font-size="20" fill="#5c6ac4" font-family="Segoe UI" font-weight="700" text-anchor="middle">+</text>
          </svg>
          <h3 class="card-title">More Tools Coming Soon</h3>
          <p class="card-desc">We are adding more conversion and compression tools frequently.</p>
          <button class="btn-action" onclick="alert('More tools coming soon!');">Stay Tuned</button>
        </article>
      </div>
    </section>

    <!-- Info Sections -->
    <section id="about" class="info-section" tabindex="0" aria-label="About PAPERPREP">
      <h2>About PAPERPREP</h2>
      <p>PAPERPREP is an innovative platform designed to make file conversions and compression effortless and efficient. Whether you are a student, professional, or a casual user, our futuristic tools help you manage documents and images with just a few clicks. Our mission is to provide a seamless and intuitive user experience with cutting edge technology and soothing design.</p>
    </section>

    <section id="privacy" class="info-section" tabindex="0" aria-label="Privacy Policy">
      <h2>Privacy Policy</h2>
      <p>Your privacy is important to us. PAPERPREP does not store or share any of your files. All conversions occur securely and temporarily with no user data retention. We use industry best practices to safeguard your information.</p>
    </section>

    <section id="contact" class="info-section" tabindex="0" aria-label="Contact Information">
      <h2>Contact Us</h2>
      <p>If you have any questions, suggestions, or need support, feel free to reach out to us at <a href="mailto:support@paperprep.com">support@paperprep.com</a>. We value your feedback.</p>
    </section>

    <section id="terms" class="info-section" tabindex="0" aria-label="Terms and Conditions">
      <h2>Terms & Conditions</h2>
      <p>By using PAPERPREP, you agree to our terms and conditions. We provide our tools "as is" without warranties. Use the services responsibly and respect intellectual property rights.</p>
    </section>
  </main>

  <footer>
    &copy; 2024 PAPERPREP. All rights reserved.
  </footer>

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
    return send_from_directory(app.static_folder, 'favicon.ico')

if __name__ == '__main__':
    # Run on all interfaces on port 5000 for easy hosting/demo
    app.run(host='0.0.0.0', port=5000)
