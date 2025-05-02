
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'docx', 'pptx'}

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/toggle-theme")
def toggle_theme():
    current = session.get("theme", "light")
    session["theme"] = "dark" if current == "light" else "light"
    return redirect(request.referrer or url_for("index"))

@app.context_processor
def inject_theme():
    return dict(theme=session.get("theme", "light"))

@app.route("/tool/<tool_name>", methods=["GET", "POST"])
def tool(tool_name):
    result_file = None
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(saved_path)
            flash("File uploaded successfully!")
        else:
            flash("Invalid file type.")
    return render_template("tool.html", tool=tool_name.replace("-", " ").title(), result=result_file)

@app.errorhandler(413)
def file_too_large(e):
    flash("File is too large. Max size is 25MB.")
    return redirect(request.referrer or url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
