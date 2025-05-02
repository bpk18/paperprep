from flask import Flask, render_template_string

app = Flask(__name__)

base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>PAPERPREP - File Conversion & Compression Tools</title>
<!-- FontAwesome CDN for icons -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
<style>
  :root {
    --primary-color-light: #4a90e2;
    --background-light: #f9fbfc;
    --card-bg-light: #ffffff;
    --text-color-light: #222222;
    --nav-bg-light: #ffffff;
    --primary-color-dark: #4a90e2;
    --background-dark: #121212;
    --card-bg-dark: #1e1e1e;
    --text-color-dark: #e0e0e0;
    --nav-bg-dark: #181818;
    --button-bg-light: linear-gradient(135deg, #6a85b6, #bac8e0);
    --button-bg-dark: linear-gradient(135deg, #375a7f, #2a4365);
    --shadow-light: 0 4px 15px rgba(74, 144, 226, 0.3);
    --shadow-dark: 0 4px 15px rgba(0,0,0,0.8);
  }

  body {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: var(--background-light);
    color: var(--text-color-light);
    transition: background-color 0.3s ease, color 0.3s ease;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  body.dark {
    background-color: var(--background-dark);
    color: var(--text-color-dark);
  }

  /* Navbar */
  nav {
    background-color: var(--nav-bg-light);
    color: var(--text-color-light);
    padding: 0.75rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    z-index: 1000;
  }
  body.dark nav {
    background-color: var(--nav-bg-dark);
    color: var(--text-color-dark);
    box-shadow: 0 2px 8px rgba(0,0,0,0.8);
  }

  .nav-brand {
    font-weight: 700;
    font-size: 1.5rem;
    letter-spacing: 0.1em;
    font-family: 'Orbitron', sans-serif;
    color: var(--primary-color-light);
  }
  body.dark .nav-brand {
    color: var(--primary-color-dark);
  }

  /* Menu button */
  .menu-btn {
    font-size: 1.5rem;
    cursor: pointer;
    display: none;
    color: inherit;
    background: none;
    border: none;
  }

  /* Navbar links */
  .nav-links {
    display: flex;
    gap: 1rem;
    list-style: none;
  }
  .nav-links a {
    color: inherit;
    text-decoration: none;
    font-weight: 600;
    font-size: 1rem;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    transition: background-color 0.3s ease;
  }
  .nav-links a:hover,
  .nav-links a:focus {
    background-color: var(--primary-color-light);
    color: #fff;
  }
  body.dark .nav-links a:hover,
  body.dark .nav-links a:focus {
    background-color: var(--primary-color-dark);
    color: #fff;
  }

  /* Theme toggle button */
  .theme-toggle {
    background: var(--button-bg-light);
    border: none;
    border-radius: 24px;
    padding: 0.4rem 0.8rem;
    color: white;
    font-weight: 600;
    cursor: pointer;
    box-shadow: var(--shadow-light);
    transition: background 0.3s ease, box-shadow 0.3s ease;
    margin-left: 1rem;
  }
  body.dark .theme-toggle {
    background: var(--button-bg-dark);
    box-shadow: var(--shadow-dark);
  }
  .theme-toggle:focus {
    outline: 2px solid var(--primary-color-light);
    outline-offset: 2px;
  }

  /* Responsive nav for mobile */
  @media (max-width: 768px) {
    .menu-btn {
      display: block;
    }
    .nav-links {
      position: fixed;
      top: 56px;
      right: 0;
      background-color: var(--nav-bg-light);
      width: 200px;
      height: calc(100% - 56px);
      flex-direction: column;
      padding: 1rem;
      gap: 1.5rem;
      transform: translateX(100%);
      transition: transform 0.3s ease;
      box-shadow: -2px 0 10px rgba(0,0,0,0.1);
    }
    body.dark .nav-links {
      background-color: var(--nav-bg-dark);
      box-shadow: -2px 0 10px rgba(0,0,0,0.8);
    }
    .nav-links.active {
      transform: translateX(0);
    }
  }

  /* Main content */
  main {
    flex: 1 0 auto;
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
  }
  h1 {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 2.75rem;
    margin-bottom: 0.5rem;
    text-align: center;
    background: linear-gradient(90deg, #4a90e2, #50e3c2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  p.subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: #666;
    max-width: 600px;
    margin: 0 auto 2rem;
  }
  body.dark p.subtitle {
    color: #aaa;
  }

  /* Tool cards grid */
  .tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
    gap: 1.5rem;
  }
  .tool-card {
    background-color: var(--card-bg-light);
    border-radius: 15px;
    box-shadow: var(--shadow-light);
    padding: 1.5rem 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    color: var(--text-color-light);
    text-align: center;
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    user-select: none;
  }
  .tool-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 8px 25px rgba(74, 144, 226, 0.5);
  }
  body.dark .tool-card {
    background-color: var(--card-bg-dark);
    color: var(--text-color-dark);
    box-shadow: var(--shadow-dark);
  }
  body.dark .tool-card:hover {
    box-shadow: 0 8px 25px rgba(74, 144, 226, 0.9);
  }

  .tool-icon {
    font-size: 3.5rem;
    margin-bottom: 0.8rem;
    background: linear-gradient(45deg, #4a90e2, #50e3c2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  body.dark .tool-icon {
    background: linear-gradient(45deg, #50e3c2, #4a90e2);
  }

  .tool-name {
    font-weight: 700;
    font-size: 1.15rem;
  }

  /* Footer */
  footer {
    text-align: center;
    padding: 1rem 0.5rem;
    font-size: 0.9rem;
    color: #777;
  }
  body.dark footer {
    color: #bbb;
  }

</style>
</head>
<body>
<nav>
  <div class="nav-brand" aria-label="Website logo and name">PAPERPREP</div>
  <button class="menu-btn" aria-label="Toggle menu" aria-expanded="false">&#9776;</button>
  <ul class="nav-links" role="menu">
    <li><a href="/about" role="menuitem" tabindex="-1">About</a></li>
    <li><a href="/privacy" role="menuitem" tabindex="-1">Privacy</a></li>
    <li><a href="/contact" role="menuitem" tabindex="-1">Contact</a></li>
    <li><a href="/terms" role="menuitem" tabindex="-1">Terms &amp; Conditions</a></li>
  </ul>
  <button class="theme-toggle" aria-label="Toggle dark mode">Dark Mode</button>
</nav>
<main>
  <h1>PAPERPREP</h1>
  <p class="subtitle">The ultimate futuristic tool hub for document & image conversions and compressions.</p>
  <section class="tools-grid" role="list" aria-label="Tools list">
    <article class="tool-card" role="listitem" tabindex="0" aria-describedby="pdf-to-word-desc" onclick="alert('This feature will be implemented soon!')">
      <i class="fa-solid fa-file-pdf tool-icon" aria-hidden="true"></i>
      <div class="tool-name">PDF to Word</div>
      <p id="pdf-to-word-desc" class="sr-only">Convert PDF documents to editable Word files</p>
    </article>
    <article class="tool-card" role="listitem" tabindex="0" aria-describedby="jpg-to-word-desc" onclick="alert('This feature will be implemented soon!')">
      <i class="fa-solid fa-image tool-icon" aria-hidden="true"></i>
      <div class="tool-name">JPG to Word</div>
      <p id="jpg-to-word-desc" class="sr-only">Convert JPG images to Word documents</p>
    </article>
    <article class="tool-card" role="listitem" tabindex="0" aria-describedby="ppt-to-pdf-desc" onclick="alert('This feature will be implemented soon!')">
      <i class="fa-solid fa-file-powerpoint tool-icon" aria-hidden="true"></i>
      <div class="tool-name">PPT to PDF</div>
      <p id="ppt-to-pdf-desc" class="sr-only">Convert Powerpoint presentations to PDF format</p>
    </article>
    <article class="tool-card" role="listitem" tabindex="0" aria-describedby="pdf-to-ppt-desc" onclick="alert('This feature will be implemented soon!')">
      <i class="fa-solid fa-file-pdf tool-icon" aria-hidden="true"></i>
      <div class="tool-name">PDF to PPT</div>
      <p id="pdf-to-ppt-desc" class="sr-only">Convert PDF files to Powerpoint presentations</p>
    </article>
    <article class="tool-card" role="listitem" tabindex="0" aria-describedby="images-to-pdf-desc" onclick="alert('This feature will be implemented soon!')">
      <i class="fa-solid fa-file-arrow-up tool-icon" aria-hidden="true"></i>
      <div class="tool-name">Multiple Images to PDF</div>
      <p id="images-to-pdf-desc" class="sr-only">Combine multiple images into a single PDF</p>
    </article>
    <article class="tool-card" role="listitem" tabindex="0" aria-describedby="merge-pdf-desc" onclick="alert('This feature will be implemented soon!')">
      <i class="fa-solid fa-file-lines tool-icon" aria-hidden="true"></i>
      <div class="tool-name">Merge PDF</div>
      <p id="merge-pdf-desc" class="sr-only">Merge multiple PDF files into one document</p>
    </article>
    <article class="tool-card" role="listitem" tabindex="0" aria-describedby="image-compressor-desc" onclick="alert('This feature will be implemented soon!')">
      <i class="fa-solid fa-compress tool-icon" aria-hidden="true"></i>
      <div class="tool-name">Image Compressor</div>
      <p id="image-compressor-desc" class="sr-only">Compress image files to reduce size</p>
    </article>
    <article class="tool-card" role="listitem" tabindex="0" aria-describedby="pdf-compressor-desc" onclick="alert('This feature will be implemented soon!')">
      <i class="fa-solid fa-compress-arrows-alt tool-icon" aria-hidden="true"></i>
      <div class="tool-name">PDF Compressor</div>
      <p id="pdf-compressor-desc" class="sr-only">Compress PDF files without losing quality</p>
    </article>
  </section>
</main>
<footer>
  &copy; 2024 PAPERPREP - All Rights Reserved
</footer>
<script>
  // Theme toggle
  const body = document.body;
  const toggleBtn = document.querySelector('.theme-toggle');
  const menuBtn = document.querySelector('.menu-btn');
  const navLinks = document.querySelector('.nav-links');

  // Load saved theme from localStorage or default light
  const savedTheme = localStorage.getItem('theme') || 'light';
  if(savedTheme === 'dark'){
    body.classList.add('dark');
    toggleBtn.textContent = 'Light Mode';
  }

  toggleBtn.addEventListener('click', () => {
    body.classList.toggle('dark');
    if(body.classList.contains('dark')){
      toggleBtn.textContent = 'Light Mode';
      localStorage.setItem('theme', 'dark');
    } else {
      toggleBtn.textContent = 'Dark Mode';
      localStorage.setItem('theme', 'light');
    }
  });

  // Menu toggle for small screens
  menuBtn.addEventListener('click', () => {
    const expanded = menuBtn.getAttribute('aria-expanded') === 'true' || false;
    menuBtn.setAttribute('aria-expanded', !expanded);
    navLinks.classList.toggle('active');

    // Manage tabindex for accessibility
    const links = navLinks.querySelectorAll('a');
    if(navLinks.classList.contains('active')){
      links.forEach(link => link.setAttribute('tabindex', '0'));
    } else {
      links.forEach(link => link.setAttribute('tabindex', '-1'));
    }
  });

  // Accessibility: close nav menu when clicking on a nav link (mobile)
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      if(window.innerWidth <= 768){
        navLinks.classList.remove('active');
        menuBtn.setAttribute('aria-expanded', 'false');
        navLinks.querySelectorAll('a').forEach(a => a.setAttribute('tabindex', '-1'));
      }
    });
  });

  // Set nav link tab indices initially for mobile
  function setInitialNavTabIndex(){
    if(window.innerWidth <= 768){
      navLinks.querySelectorAll('a').forEach(a => a.setAttribute('tabindex', '-1'));
    } else {
      navLinks.querySelectorAll('a').forEach(a => a.setAttribute('tabindex', '0'));
      navLinks.classList.remove('active');
      menuBtn.setAttribute('aria-expanded', 'false');
    }
  }
  window.addEventListener('resize', setInitialNavTabIndex);
  setInitialNavTabIndex();
</script>
</body>
</html>
"""

simple_page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{{ title }} - PAPERPREP</title>
<style>
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-width: 700px;
    margin: 3rem auto 2rem;
    padding: 0 1rem;
    color: #222;
  }
  h1 {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 2rem;
    color: #4a90e2;
    margin-bottom: 1rem;
  }
  a.home-link {
    display: inline-block;
    margin-top: 2rem;
    color: #4a90e2;
    text-decoration: none;
    font-weight: 600;
  }
  a.home-link:hover, a.home-link:focus {
    text-decoration: underline;
  }
  p {
    line-height: 1.5;
  }
</style>
</head>
<body>
<h1>{{ title }}</h1>
<div>
  {{ content|safe }}
</div>
<a href="/" class="home-link" aria-label="Go back to homepage">&larr; Back to Home</a>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(base_template)

@app.route('/about')
def about():
    content = """
    <p>Welcome to PAPERPREP, your futuristic web platform designed to simplify your document and image conversion needs.
    We aim to provide fast, easy, and reliable tools to enhance your productivity.</p>
    <p>This platform is developed as a college project with a focus on user-centered design and modern UI patterns.</p>
    """
    return render_template_string(simple_page_template, title="About Us", content=content)

@app.route('/privacy')
def privacy():
    content = """
    <p>Your privacy is important to us. PAPERPREP does not collect or store any personal information or files uploaded to the tools.
    All processing happens client-side or on your device to ensure maximum confidentiality.</p>
    <p>Please avoid uploading sensitive documents unless you trust the platform or have secured your connection.</p>
    """
    return render_template_string(simple_page_template, title="Privacy Policy", content=content)

@app.route('/contact')
def contact():
    content = """
    <p>If you have any questions, feedback, or issues, feel free to reach out to us at:</p>
    <ul>
        <li>Email: <a href="mailto:support@paperprep.com">support@paperprep.com</a></li>
        <li>Phone: +1-234-567-8901</li>
    </ul>
    <p>We appreciate your interest and will respond as soon as possible.</p>
    """
    return render_template_string(simple_page_template, title="Contact Us", content=content)

@app.route('/terms')
def terms():
    content = """
    <p>By using PAPERPREP, you agree that the platform is provided as-is and without warranties.
    We are not liable for any data loss or damages resulting from the use of the tools.</p>
    <p>Please read carefully and use the services responsibly.</p>
    """
    return render_template_string(simple_page_template, title="Terms and Conditions", content=content)

if __name__ == '__main__':
    app.run(debug=True,port=5000)
