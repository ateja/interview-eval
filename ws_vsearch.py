from flask import Flask, request, jsonify
from vectordb import VectorInterviewDb
import os
import numpy as np

app = Flask(__name__)

# Initialize the vector database
VECTOR_DB_FILE = "docs/interview_questions.xlsx"
vector_db = VectorInterviewDb(VECTOR_DB_FILE)

@app.route("/index", methods=["POST"])
def index_documents():
    """
    Endpoint to index interview questions from the given document.
    """
    try:
        if os.path.exists(vector_db.FAISS_INDEX_FILE):
            os.remove(vector_db.FAISS_INDEX_FILE)
        vector_db.populate_index()
        return jsonify({"message": "Indexing completed successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search", methods=["GET"])
def search_documents():
    """
    Endpoint to search for relevant interview questions using FAISS.
    """
    query = request.args.get("query")
    top_k = int(request.args.get("top_k", 5))

    if not query:
        return jsonify({"error": "Query parameter is required."}), 400

    try:
        results = vector_db.search_faiss(query, top_k=top_k)

        # Convert DataFrame to a JSON-serializable format
        search_results = results.to_dict(orient="records")

        # Ensure no NumPy arrays are in the response
        for item in search_results:
            for key, value in item.items():
                if isinstance(value, np.ndarray):  # Convert ndarray to list
                    item[key] = value.tolist()

        return jsonify({"results": search_results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)