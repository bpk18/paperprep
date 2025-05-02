
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
ALLOWED = {'pdf', 'jpg', 'jpeg', 'png', 'docx', 'pptx'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED

@app.route("/")
def index(): return render_template("index.html")

@app.route("/toggle-theme")
def toggle_theme():
    session["theme"] = "dark" if session.get("theme", "light") == "light" else "light"
    return redirect(request.referrer or "/")

@app.context_processor
def inject_theme(): return dict(theme=session.get("theme", "light"))

@app.route("/tool/<tool_name>", methods=["GET", "POST"])
def tool(tool_name):
    if request.method == "POST":
        file = request.files.get("file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            flash("File uploaded successfully!")
        else:
            flash("Invalid or missing file.")
    return render_template("tool.html", tool=tool_name.replace("-", " ").title())

@app.route("/about")   def about(): return render_template("about.html", title="About")
@app.route("/privacy") def privacy(): return render_template("privacy.html", title="Privacy")
@app.route("/contact") def contact(): return render_template("contact.html", title="Contact")
@app.route("/terms")   def terms(): return render_template("terms.html", title="Terms & Conditions")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
