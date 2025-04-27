from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
import openpyxl
from fpdf import FPDF

app = Flask(__name__)

# Set upload folder and converted folder
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/excel-to-pdf', methods=['GET', 'POST'])
def excel_to_pdf():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.xlsx'):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            # Read Excel file
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active

            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            for row in sheet.iter_rows(values_only=True):
                row_text = " | ".join(map(str, row))
                pdf.cell(200, 10, txt=row_text, ln=True)

            output_path = os.path.join(app.config['CONVERTED_FOLDER'], filename.replace('.xlsx', '.pdf'))
            pdf.output(output_path)

            return send_file(output_path, as_attachment=True)
    return render_template('excel_to_pdf.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Ensure the app runs on port 5000
