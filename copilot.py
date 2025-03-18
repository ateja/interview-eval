from vectordb import VectorInterviewDb
from openai import OpenAI
from promptRenderer import PromptRenderer
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewCopilot:
    def __init__(self, prompt_template: str, vector_db: VectorInterviewDb, openai_client: OpenAI):
        """
        Initializes the InterviewCopilot class.
        :param prompt_template: Jinja2 template for prompt rendering.
        :param vector_db: Instance of VectorInterviewDb for RAG retrieval.
        :param openai_client: OpenAI client instance for LLM interactions.
        """
        self.renderer = PromptRenderer(prompt_template)
        self.vector_db = vector_db
        self.openai_client = openai_client

    def process_query(self, user_query: str, pdf_text: str, sample_pdf_text: str = "", sample_json: str = "{}") -> str:
        """
        Processes the user query using RAG and OpenAI LLM.
        :param user_query: The query string provided by the user.
        :param pdf_text: The text extracted from the PDF document.
        :param sample_pdf_text: Example PDF text for the template.
        :param sample_json: Example JSON for the template.
        :return: AI-generated response.
        """
        rag_results = self.vector_db.search_faiss(user_query, top_k=5)
        formatted_rag_results = [result['chunk'] for _, result in rag_results.iterrows()]
        
        prompt = self.renderer.render(
            user_query=user_query,
            single_shot_prompt_pdf_text=sample_pdf_text,
            single_shot_prompt_json=sample_json,
            input_pdf_text=pdf_text,
            rag_results=formatted_rag_results
        )
        
        logger.info("Sending prompt to OpenAI:\n%s", prompt)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an AI interview assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return response.choices[0].message.content

# Example template
jinja_template = """
User Query: {{ user_query }}

Single-Shot Prompt (PDF):
{{ single_shot_prompt_pdf_text }}

Single-Shot Prompt (JSON):
{% for key, value in single_shot_prompt_json.items() %}
  {{ key }}: {{ value }}
{% endfor %}

Input PDF Text:
{{ input_pdf_text }}

RAG Results:
{% for result in rag_results %}
  - {{ result }}
{% endfor %}
"""

# Example usage
if __name__ == "__main__":
    openai_key = os.environ["openai_key"]
    vector_db = VectorInterviewDb("docs/interview_questions.xlsx")
    if(vector_db.reindex_needed):
        ve
    openai_client = OpenAI(api_key=openai_key)
    copilot = InterviewCopilot(jinja_template, vector_db, openai_client)
    user_query = "What are the key takeaways from the document?"
    input_pdf_text = "Artificial Intelligence has transformed various industries."
    response = copilot.process_query(user_query, input_pdf_text)
    print(response)
