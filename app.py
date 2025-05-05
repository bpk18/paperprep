from flask import Flask, request, redirect, url_for, render_template_string, flash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Needed for flash messages

# Tool list with route and display names and icons (using Font Awesome)
tools = [
    {"name":"PDF to Word", "route":"pdf_to_word", "icon":"fas fa-file-pdf"},
    {"name":"JPG to Word", "route":"jpg_to_word", "icon":"fas fa-file-image"},
    {"name":"PPT to PDF", "route":"ppt_to_pdf", "icon":"fas fa-file-powerpoint"},
    {"name":"PDF to PPT", "route":"pdf_to_ppt", "icon":"fas fa-file-pdf"},
    {"name":"Multiple Images to One PDF", "route":"images_to_pdf", "icon":"fas fa-file-image"},
    {"name":"Merge PDF", "route":"merge_pdf", "icon":"fas fa-file-pdf"},
    {"name":"Image Compressor", "route":"image_compressor", "icon":"fas fa-compress"},
    {"name":"PDF Compressor", "route":"pdf_compressor", "icon":"fas fa-compress"},
    # Add more tools here if needed
]

# Base HTML template with placeholders for page content and title
base_template = """
<!DOCTYPE html>
<html lang="en" {% if dark_mode %}class="dark-theme"{% endif %}>
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1,user-scalable=no" />
    <meta name="description" content="PAPERPREP - Fast and reliable document conversion tools including {% for tool in tools %}{{tool.name}}{% if not loop.last %}, {% endif %}{% endfor %}." />
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon" />
    <title>PAPERPREP - {{ title }}</title>
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" />
    <!-- Bootstrap CSS -->
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet" />
    <style>
        /* Light theme */
        body {
            background: #f0f4f8;
            color: #121212;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }
        /* Dark theme overrides */
        html.dark-theme body {
            background: #121212;
            color: #e0e0e0;
        }
        .navbar {
            background-color: #0d6efd;
            transition: background-color 0.3s ease;
        }
        html.dark-theme .navbar {
            background-color: #0a58ca;
        }
        .navbar-brand, .nav-link, .navbar-toggler-icon {
            color: white !important;
        }
        .nav-link:hover {
            text-decoration: underline;
        }
        .btn-primary {
            background: linear-gradient(45deg, #4facfe, #00f2fe);
            border: none;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.5);
            font-weight: 600;
            transition: background 0.3s ease, transform 0.2s ease;
        }
        .btn-primary:hover {
            background: linear-gradient(45deg, #00f2fe, #4facfe);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 242, 254, 0.7);
        }
        .btn-toggle {
            background: #198754;
            border: none;
            color: white;
            padding: 0.375rem 0.75rem;
            font-weight: 600;
            border-radius: 0.375rem;
            box-shadow: 0 4px 12px rgba(25, 135, 84, 0.6);
            cursor: pointer;
            transition: background-color 0.3s ease;
            user-select: none;
        }
        .btn-toggle:hover {
            background-color: #158247;
        }
        html.dark-theme .btn-toggle {
            background-color: #0dcaf0;
            box-shadow: 0 4px 12px rgba(13, 202, 240, 0.7);
            color: #121212;
        }
        html.dark-theme .btn-toggle:hover {
            background-color: #0bb9e6;
        }
        .container {
            max-width: 540px;
            margin-top: 3rem;
            margin-bottom: 3rem;
        }
        h1, h2 {
            font-weight: 700;
            letter-spacing: 0.06em;
        }
        .tool-list {
            margin-top: 2rem;
        }
        .card-tool {
            cursor: pointer;
            border-radius: 12px;
            box-shadow: 0 7px 25px rgba(0,0,0,0.11);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            background: white;
        }
        html.dark-theme .card-tool {
            background: #1e1e1e;
            box-shadow: 0 7px 25px rgba(13,202,240,0.3);
        }
        .card-tool:hover {
            transform: translateY(-6px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.2);
        }
        html.dark-theme .card-tool:hover {
            box-shadow: 0 15px 45px rgba(13,202,240,0.6);
        }
        .card-icon {
            font-size: 2.8rem;
            color: #0d6efd;
            margin-bottom: 1rem;
        }
        html.dark-theme .card-icon {
            color: #0dcaf0;
        }
        .form-file {
            margin-bottom: 1rem;
        }
        input[type="file"] {
            display: none;
        }
        label.custom-file-upload {
            display: inline-block;
            padding: 10px 20px;
            cursor: pointer;
            background: linear-gradient(45deg, #4facfe, #00f2fe);
            border-radius: 8px;
            color: white;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.5);
            transition: background 0.3s ease;
        }
        label.custom-file-upload:hover {
            background: linear-gradient(45deg, #00f2fe, #4facfe);
        }
        .animation-area {
            margin-top: 1rem;
            height: 4rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #198754;
            font-weight: 700;
            font-size: 1.2rem;
            user-select: none;
        }
        html.dark-theme .animation-area {
            color: #0dcaf0;
        }
        /* Animations for loading */
        .lds-ring {
          display: inline-block;
          position: relative;
          width: 48px;
          height: 48px;
        }
        .lds-ring div {
          box-sizing: border-box;
          display: block;
          position: absolute;
          width: 40px;
          height: 40px;
          margin: 4px;
          border: 4px solid #198754;
          border-radius: 50%;
          animation: lds-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
          border-color: #198754 transparent transparent transparent;
        }
        html.dark-theme .lds-ring div {
            border-color: #0dcaf0 transparent transparent transparent;
        }
        .lds-ring div:nth-child(1) {
          animation-delay: -0.45s;
        }
        .lds-ring div:nth-child(2) {
          animation-delay: -0.3s;
        }
        .lds-ring div:nth-child(3) {
          animation-delay: -0.15s;
        }
        @keyframes lds-ring {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
        /* Responsive adjustments */
        @media (max-width: 576px) {
            .container {
                max-width: 90vw;
            }
        }
    </style>
    {% block head_extra %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg">
        <a class="navbar-brand font-weight-bold" href="{{ url_for('home') }}">PAPERPREP</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarMenu" 
                aria-controls="navbarMenu" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon" style="filter: invert(1);"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarMenu">
            <ul class="navbar-nav mr-auto mt-2 mt-lg-0">
                <li class="nav-item"><a class="nav-link" href="#">About</a></li>
                <li class="nav-item"><a class="nav-link" href="#">Privacy</a></li>
                <li class="nav-item"><a class="nav-link" href="#">Contact</a></li>
                <li class="nav-item"><a class="nav-link" href="#">Terms and Conditions</a></li>
            </ul>
            <button id="theme-toggle" class="btn btn-toggle" aria-label="Toggle light and dark mode">Dark Mode</button>
        </div>
    </nav>

    <main class="container">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert alert-info mt-3" role="alert">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </main>

    <footer class="text-center text-muted pb-3">
        &copy; 2024 PAPERPREP - All rights reserved.
    </footer>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script>
        const themeToggleBtn = document.getElementById('theme-toggle');
        const htmlElem = document.documentElement;

        // Initialize theme from localStorage or default (light)
        if(localStorage.getItem('darkMode') === 'true'){
            htmlElem.classList.add('dark-theme');
            themeToggleBtn.textContent = 'Light Mode';
        }

        themeToggleBtn.addEventListener('click', () => {
            htmlElem.classList.toggle('dark-theme');
            const isDark = htmlElem.classList.contains('dark-theme');
            themeToggleBtn.textContent = isDark ? 'Light Mode' : 'Dark Mode';
            localStorage.setItem('darkMode', isDark);
        });

        // Basic animation for upload input field
        const fileInput = document.querySelector('input[type="file"]');
        if(fileInput){
            fileInput.addEventListener('change', () => {
                if(fileInput.files.length > 0){
                    const animArea = document.getElementById('animation-area');
                    if(animArea){
                        animArea.innerHTML = '<div class="lds-ring"><div></div><div></div><div></div><div></div></div> Uploading...';
                    }
                }
            });
        }
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""

# Home page displays list of tools with icons and links
@app.route('/')
def home():
    content = """
    <h1 class="text-center">Welcome to PAPERPREP</h1>
    <p class="lead text-center">Choose from the powerful document and image conversion tools below</p>
    <div class="tool-list">
        {% for tool in tools %}
        <a href="{{ url_for(tool.route) }}" aria-label="Open {{ tool.name }}" style="text-decoration:none; color: inherit;">
            <div class="card-tool d-flex align-items-center">
                <i class="card-icon {{ tool.icon }}" aria-hidden="true"></i>
                <div class="ml-3" style="font-size:1.3rem; font-weight:600;">{{ tool.name }}</div>
            </div>
        </a>
        {% endfor %}
    </div>
    """
    return render_template_string(base_template, title="Home", tools=tools, dark_mode=False, content=content, 
                                  **{'block content': content})

def tool_page_template(tool):
    # Template for tool pages with file upload and dummy conversion button and animations
    return """
    <h2 class="text-center mb-4">{{ tool.name }}</h2>
    <form action="{{ url_for(tool.route) }}" method='post' enctype='multipart/form-data'>
        <label for="file-upload" class="custom-file-upload" aria-label="Upload file for {{ tool.name }}">
            <i class="fas fa-upload"></i> Select File
        </label>
        <input id="file-upload" type="file" name="file" required aria-required="true" accept="*/*"/>
        <button type="submit" class="btn btn-primary btn-block mt-3" aria-label="Convert file for {{ tool.name }}">Convert</button>
        <div id="animation-area" class="animation-area" aria-live="polite" aria-atomic="true"></div>
    </form>
    {% if success %}
        <div class="alert alert-success mt-3" role="alert" aria-live="polite" aria-atomic="true">
            Conversion successful! Download link would appear here.
        </div>
    {% endif %}
    <p class="text-muted mt-4" style="font-size: 0.9rem;">
        Note: This demo app does not perform actual file conversions. You can implement your conversion logic in <code>app.py</code>.
    </p>
    """

# Correct dynamic route generator fixing late binding by using default argument
def create_tool_view(tool):
    def view_func():
        if request.method == 'POST':
            file = request.files.get('file')
            if not file or file.filename == '':
                flash('No file selected for conversion', 'error')
                return redirect(request.url)
            # Dummy success - implement actual logic here
            success = True
            return render_template_string(
                base_template,
                title=tool['name'],
                tools=tools,
                dark_mode=False,
                success=success,
                tool=tool,
                content=tool_page_template(tool),
                **{'block content': tool_page_template(tool)}
            )
        return render_template_string(
            base_template,
            title=tool['name'],
            tools=tools,
            dark_mode=False,
            success=False,
            tool=tool,
            content=tool_page_template(tool),
            **{'block content': tool_page_template(tool)}
        )
    view_func.__name__ = tool['route']
    view_func.methods = ['GET', 'POST']
    return view_func

for tool in tools:
    route_path = '/' + tool['route']
    app.add_url_rule(route_path, view_func=create_tool_view(tool), methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
