from flask import Flask, request, jsonify
import os
import json
from pdf_to_json import PDFTextExtractor
# Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = file.filename.replace(" ", "_")  # Basic filename sanitization
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        extractor = PDFTextExtractor(file_path)
        feedback_json = extractor.get_json_feedback()
        
        return jsonify(json.loads(feedback_json))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
