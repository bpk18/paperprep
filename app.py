from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pdf-to-word', methods=['GET', 'POST'])
def pdf_to_word():
    if request.method == 'POST':
        # Handle PDF to Word conversion
        pass
    return render_template('tools/pdf_to_word.html')

if __name__ == '__main__':
    app.run(debug=True)