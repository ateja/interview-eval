from vectordb import VectorInterviewDb
from openai import OpenAI
from promptRenderer import PromptRenderer
import os
import logging
from jinja2 import Template
import json
import tiktoken
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI API key from .env file
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

vector_db = VectorInterviewDb("docs/interview_questions.xlsx")

VSEARCH_URL = os.getenv('VSEARCH_URL', 'http://localhost:5000/search')
PROMPT_RENDERER_URL = os.getenv('PROMPT_RENDERER_URL', 'http://localhost:5001/render')

class InterviewCopilot:
    def __init__(self, prompt_template: str, vector_db: VectorInterviewDb):
        """
        Initializes the InterviewCopilot class.
        :param prompt_template: Jinja2 template for prompt rendering.
        :param vector_db: Instance of VectorInterviewDb for RAG retrieval.
        """
        self.renderer = PromptRenderer(prompt_template)
        self.vector_db = vector_db
        self.openai_client = OpenAI(api_key=openai_key)

    def process_query(self, user_query: str, pdf_text: str, sample_pdf_text: str = "", sample_json: str = "{}") -> str:
        """
        Processes the user query using RAG and OpenAI LLM.
        :param user_query: The query string provided by the user.
        :param pdf_text: The text extracted from the PDF document.
        :param sample_pdf_text: Example PDF text for the template.
        :param sample_json: Example JSON for the template.
        :return: AI-generated response.
        """
        # Call the remote search endpoint
        response = requests.get(
            VSEARCH_URL,
            params={
                "query": user_query,
                "top_k": 5
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Search request failed: {response.text}")
        
        search_results = response.json()["results"]
        formatted_rag_results = [result['chunk'] for result in search_results]

        # Call the remote render endpoint
        render_data = {
            "user_query": user_query,
            "single_shot_prompt_pdf_text": sample_pdf_text,
            "single_shot_prompt_json": sample_json,
            "input_pdf_text": pdf_text,
            "rag_results": formatted_rag_results
        }
        
        response = requests.post(
            PROMPT_RENDERER_URL,
            json=render_data
        )
        
        if response.status_code != 200:
            raise Exception(f"Render request failed: {response.text}")
        
        prompt = response.json()["rendered_prompt"]

        logger.info("Prompt:**********************************\n%s", prompt)
        logger.info("Prompt:**********************************\n")

        logger.info("Sending prompt to OpenAI:\n%s", prompt)

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI interview assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    if vector_db.reindex_needed:
        vector_db.populate_index()
    copilot = InterviewCopilot("prompt.jinja2", vector_db)
    user_query = "Extract all programming questions and responses from this interview feedback"
    input_pdf_text = "Artificial Intelligence has transformed various industries."
    response = copilot.process_query(user_query, input_pdf_text)
    print(response)
