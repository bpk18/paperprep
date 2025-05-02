from flask import Flask, render_template, request, redirect, flash, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages

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

@app.route('/process', methods=['POST'])
def process():
    tool = request.form.get('tool')
    uploaded_file = request.files.get('file')

    if not uploaded_file or uploaded_file.filename == '':
        flash('Please upload a file.', 'danger')
        return redirect(url_for('index'))

    # Simulate file processing
    print(f"Processing file: {uploaded_file.filename} with tool: {tool}")
    flash(f"Success! File '{uploaded_file.filename}' was processed using '{tool}'.", 'success')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
