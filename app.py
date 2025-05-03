from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory

app = Flask(__name__)

# Base HTML layout with navbar, theme toggle, menu and content block with SEO improvements and favicon link
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
          margin: 0 auto;
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

        /* Form styles for contact */
        form {
          max-width: 500px;
          margin: 0 auto;
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
        input[type="text"], input[type="email"], textarea {
          padding: 0.5rem 0.8rem;
          border-radius: 8px;
          border: 1px solid var(--border-color);
          font-size: 1rem;
          background-color: var(--card-bg);
          color: var(--text);
          resize: vertical;
          transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="email"]:focus, textarea:focus {
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
        </div>
        <button class="theme-toggle-btn" id="theme-toggle" aria-label="Toggle dark/light theme">Dark Theme</button>
    </nav>
    <main>
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

# Home page with tools listed
home_html = '''
{% extends 'base.html' %}
{% block content %}
    <h1>Welcome to PAPERPREP</h1>
    <p class="lead">Your all-in-one document and image conversion toolkit with a futuristic UI and seamless experience.</p>
    <section class="tools-grid" aria-label="Conversion Tools">

        <!-- PDF to Word -->
        <article class="tool-card" role="listitem" aria-label="PDF to Word conversion tool">
            <svg class="tool-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <path d="M48 4H16a4 4 0 0 0-4 4v48a4 4 0 0 0 4 4h32a4 4 0 0 0 4-4V12l-12-8zM16 56V8h29.3L48 12v44H16z"/>
                <path d="M24 28h16v4H24zm0 8h11v4H24z" fill="var(--primary)"/>
            </svg>
            <div class="tool-name">PDF to Word</div>
            <button class="btn" onclick="alert('PDF to Word tool coming soon!')">Open</button>
        </article>

        <!-- JPG to Word -->
        <article class="tool-card" role="listitem" aria-label="JPG to Word conversion tool">
            <svg class="tool-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <circle cx="32" cy="26" r="8" stroke="var(--primary)" stroke-width="3" fill="none"/>
                <path d="M16 44h32v6H16z" fill="var(--primary)"/>
                <path d="M8 54h48v4H8z" fill="var(--secondary)"/>
            </svg>
            <div class="tool-name">JPG to Word</div>
            <button class="btn" onclick="alert('JPG to Word tool coming soon!')">Open</button>
        </article>

        <!-- PPT to PDF -->
        <article class="tool-card" role="listitem" aria-label="PPT to PDF conversion tool">
            <svg class="tool-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <rect x="14" y="12" width="36" height="40" rx="3" ry="3" fill="var(--primary)"/>
                <path fill="var(--btn-text)" d="M22 20h20v24H22z"/>
                <rect x="22" y="20" width="16" height="2" fill="var(--primary)"/>
                <rect x="22" y="35" width="16" height="2" fill="var(--primary)"/>
            </svg>
            <div class="tool-name">PPT to PDF</div>
            <button class="btn" onclick="alert('PPT to PDF tool coming soon!')">Open</button>
        </article>

        <!-- PDF to PPT -->
        <article class="tool-card" role="listitem" aria-label="PDF to PPT conversion tool">
            <svg class="tool-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <rect x="14" y="12" width="36" height="40" rx="3" ry="3" fill="var(--primary)"/>
                <path fill="var(--btn-text)" d="M22 20h20v24H22z"/>
                <path d="M26 24h12v16H26z" fill="var(--primary)"/>
            </svg>
            <div class="tool-name">PDF to PPT</div>
            <button class="btn" onclick="alert('PDF to PPT tool coming soon!')">Open</button>
        </article>

        <!-- Multiple images to one PDF -->
        <article class="tool-card" role="listitem" aria-label="Multiple images to PDF conversion tool">
            <svg class="tool-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <rect x="10" y="14" width="44" height="36" rx="4" ry="4" fill="var(--primary)"/>
                <circle cx="32" cy="32" r="8" fill="var(--btn-text)"/>
                <path d="M24 40h16v4H24z" fill="var(--primary)"/>
            </svg>
            <div class="tool-name">Images to PDF</div>
            <button class="btn" onclick="alert('Images to PDF tool coming soon!')">Open</button>
        </article>

        <!-- Merge PDF -->
        <article class="tool-card" role="listitem" aria-label="Merge PDF tool">
            <svg class="tool-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
                <rect x="8" y="14" width="48" height="36" rx="4" ry="4" fill="var(--primary)"/>
                <path d="M20 24h24v4H20zM20 34h24v4H20z" fill="var(--btn-text)"/>
            </svg>
            <div class="tool-name">Merge PDF</div>
            <button class="btn" onclick="alert('Merge PDF tool coming soon!')">Open</button>
        </article>

        <!-- Image Compressor -->
        <article class="tool-card" role="listitem" aria-label="Image Compressor tool">
            <svg class="tool-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <circle cx="32" cy="32" r="20" stroke="var(--primary)" stroke-width="4" fill="none"/>
                <path d="M22 32l6 6 12-12" stroke="var(--primary)" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="tool-name">Image Compressor</div>
            <button class="btn" onclick="alert('Image Compressor tool coming soon!')">Open</button>
        </article>

        <!-- PDF Compressor -->
        <article class="tool-card" role="listitem" aria-label="PDF Compressor tool">
            <svg class="tool-icon" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <rect x="16" y="16" width="32" height="32" fill="var(--primary)" rx="6" ry="6"/>
                <path d="M24 24h16v16H24z" fill="var(--btn-text)"/>
                <path d="M24 24h16v4H24z" fill="var(--primary)"/>
            </svg>
            <div class="tool-name">PDF Compressor</div>
            <button class="btn" onclick="alert('PDF Compressor tool coming soon!')">Open</button>
        </article>

        <!-- Placeholder for other tools -->
        <article class="tool-card" role="listitem" aria-label="More tools coming soon">
            <svg class="tool-icon" viewBox="0 0 24 24" fill="var(--primary)" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <circle cx="12" cy="12" r="10" stroke="var(--primary)" stroke-width="1" fill="none"/>
                <line x1="8" y1="12" x2="16" y2="12" stroke="var(--primary)" stroke-width="2" stroke-linecap="round"/>
                <line x1="12" y1="8" x2="12" y2="16" stroke="var(--primary)" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <div class="tool-name">More Tools Soon</div>
            <button class="btn" onclick="alert('More tools coming soon!')">Open</button>
        </article>

    </section>
{% endblock %}
'''

# About page content
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

# Privacy page
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

# Contact page with simple form (no backend submission, just alert)
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

# Terms page content
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

# Serve favicon.ico from static folder
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')


# Register templates in Flask's template loader
from jinja2 import DictLoader
app.jinja_loader = DictLoader({
    'base.html': base_html,
    'home.html': home_html,
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

if __name__ == '__main__':
    # Use 0.0.0.0 as host to be accessible externally; port 5000 is default but set explicitly
    app.run(host='0.0.0.0', port=5000, debug=True)
