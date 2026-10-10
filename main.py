import os
import json
from io import BytesIO
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
CORS(app) 

def mock_vision_ai_ocr(image_bytes, mode):
    if mode == "Excel":
        return [
            {"Student/Employee ID": "STU-992", "Scanned Written Word": "Assignment 1", "Status": "Pass"},
            {"Student/Employee ID": "STU-104", "Scanned Written Word": "Lab Grid Data", "Status": "Review"}
        ]
    return "Transcribed Scanned Word Document:\n\nThis is a sample of the text layout accurately processed from the written page by the application core backend engine."

@app.route('/api/scan', methods=['POST'])
def scan_handler():
    if 'image' not in request.files:
        return jsonify({"error": "Please provide an image asset file"}), 400

    file_bytes = request.files['image'].read()
    requested_format = request.form.get('format', 'PDF')

    ai_data = mock_vision_ai_ocr(file_bytes, requested_format)
    file_buffer = BytesIO()

    if requested_format == "Excel":
        df = pd.DataFrame(ai_data)
        with pd.ExcelWriter(file_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        file_buffer.seek(0)
        return send_file(file_buffer, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", download_name="scanned_matrix.xlsx", as_attachment=True)

    else:
        doc = SimpleDocTemplate(file_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(ai_data.replace('\n', '<br/>'), styles['Normal']), Spacer(1, 12)]
        doc.build(story)
        file_buffer.seek(0)
        return send_file(file_buffer, mimetype="application/pdf", download_name="scanned_document.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
