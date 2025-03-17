from flask import Flask, request, jsonify
from promptRenderer import PromptRenderer
import json

app = Flask(__name__)

# Load Jinja2 template from file
with open("prompt.jinja2", "r") as file:
    jinja_template = file.read()

# Initialize the PromptRenderer
renderer = PromptRenderer(jinja_template)

@app.route("/render", methods=["POST"])
def render_prompt():
    """
    Endpoint to render a prompt using Jinja2 template.
    """
    try:
        data = request.get_json()
        user_query = data.get("user_query", "")
        single_shot_prompt_pdf_text = data.get("single_shot_prompt_pdf_text", "")
        single_shot_prompt_json = data.get("single_shot_prompt_json", "{}")
        input_pdf_text = data.get("input_pdf_text", "")
        rag_results = data.get("rag_results", [])

        if not isinstance(rag_results, list):
            return jsonify({"error": "rag_results should be a list"}), 400
        
        rendered_prompt = renderer.render(
            user_query,
            single_shot_prompt_pdf_text,
            single_shot_prompt_json,
            input_pdf_text,
            rag_results
        )
        
        return jsonify({"rendered_prompt": rendered_prompt}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
