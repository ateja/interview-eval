from flask import Flask, request, jsonify
import requests
from openai import OpenAI
from vectordb import VectorInterviewDb
from copilot import InterviewCopilot
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize dependencies
VECTOR_DB_FILE = "docs/interview_questions.xlsx"
vector_db = VectorInterviewDb(VECTOR_DB_FILE)

# Load Jinja2 template from file
with open("prompt.jinja2", "r") as file:
    jinja_template = file.read()

# Load sample data from files
with open("docs/training data/sample_pdf.txt", "r") as file:
    SAMPLE_PDF_TEXT = file.read()

with open("docs/training data/sample_questions_from_pdf.json", "r") as file:
    SAMPLE_JSON = json.dumps(json.load(file))  # Convert dict to JSON string

# Initialize OpenAI client and copilot
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
copilot = InterviewCopilot(jinja_template, vector_db, openai_client)

PDF_TO_JSON_URL = "http://localhost:5002/upload"

@app.route("/copilot", methods=["POST"])
def process_copilot():
    """
    Endpoint to process user query, retrieve relevant data using RAG, 
    and generate a response using the copilot.
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        user_query = request.form.get("query", "")
        
        if not user_query:
            return jsonify({"error": "Query parameter is required."}), 400
        
        # Convert PDF to JSON
        pdf_response = requests.post(PDF_TO_JSON_URL, files={"file": file})
        if pdf_response.status_code != 200:
            return jsonify({"error": "Failed to process PDF"}), pdf_response.status_code
        
        # Handle list response from PDF service
        pdf_contents = pdf_response.json()
        pdf_text = pdf_contents[0].get("content", "") if pdf_contents else ""
        
        # Process query using copilot
        logger.info("PDF Text extracted: %s", pdf_text[:200] + "..." if len(pdf_text) > 200 else pdf_text)
        logger.info("User Query: %s", user_query)
        
        response = copilot.process_query(user_query, pdf_text, sample_pdf_text=SAMPLE_PDF_TEXT, sample_json=SAMPLE_JSON)
        
        return jsonify({"response": response}), 200
    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)