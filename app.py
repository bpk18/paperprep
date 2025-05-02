
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/tools/<tool>')
def tool_page(tool):
    tool_names = {
        'pdf-to-word': 'PDF to Word',
        'images-to-pdf': 'Multiple Images to PDF',
        'ppt-to-pdf': 'PPT to PDF',
        'pdf-to-ppt': 'PDF to PPT',
        'word-to-pdf': 'Word to PDF',
        'image-resizer': 'Image Resizer',
        'pdf-compressor': 'PDF Compressor'
    }
    if tool not in tool_names:
        return render_template('404.html'), 404
    return render_template('tool.html', tool_route=tool, tool_name=tool_names[tool])

@app.route('/process', methods=['POST'])
def process():
    tool = request.form.get('tool')
    uploaded_file = request.files.get('file')

    if uploaded_file and tool:
        filename = secure_filename(uploaded_file.filename)
        print(f"Received file: {filename} for tool: {tool}")
        flash(f"Successfully processed '{filename}' using the '{tool}' tool!", 'success')
    else:
        flash('Please select a file and a tool to process.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
