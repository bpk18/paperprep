from flask import Flask, render_template, session

app = Flask(__name__)
app.secret_key = "secret"

@app.before_request
def set_theme():
    if "theme" not in session:
        session["theme"] = "light"

@app.route("/set_theme/<theme>")
def set_theme_route(theme):
    session["theme"] = theme
    return ("", 204)

@app.route("/")
def index():
    return render_template("index.html", theme=session["theme"])

@app.route("/about")
def about():
    return render_template("about.html", theme=session["theme"])

@app.route("/privacy")
def privacy():
    return render_template("privacy.html", theme=session["theme"])

@app.route("/contact")
def contact():
    return render_template("contact.html", theme=session["theme"])

@app.route("/terms")
def terms():
    return render_template("terms.html", theme=session["theme"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
