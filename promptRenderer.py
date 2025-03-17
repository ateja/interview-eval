from jinja2 import Template
import json

class PromptRenderer:
    def __init__(self, template_str: str):
        """
        Initializes the PromptRenderer with a Jinja2 template string.
        :param template_str: The Jinja2 template for rendering the prompt.
        """
        self.template = Template(template_str)

    def render(self, user_query: str, single_shot_prompt_pdf_text: str, single_shot_prompt_json: str, 
               input_pdf_text: str, rag_results: list) -> str:
        """
        Renders the prompt using the provided inputs.
        :param user_query: The query string provided by the user.
        :param single_shot_prompt_pdf_text: Text from a single-shot prompt PDF.
        :param single_shot_prompt_json: JSON formatted single-shot prompt.
        :param input_pdf_text: Extracted text from an input PDF.
        :param rag_results: A list of results retrieved using RAG (retrieval-augmented generation).
        :return: The rendered prompt string.
        """
        try:
            single_shot_prompt_dict = json.loads(single_shot_prompt_json)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for single_shot_prompt_json")
        
        return self.template.render(
            user_query=user_query,
            single_shot_prompt_pdf_text=single_shot_prompt_pdf_text,
            single_shot_prompt_json=single_shot_prompt_dict,
            input_pdf_text=input_pdf_text,
            rag_results=rag_results
        )

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
    renderer = PromptRenderer(jinja_template)
    user_query = "What are the key takeaways from the document?"
    single_shot_prompt_pdf_text = "This document provides an overview of AI models."
    single_shot_prompt_json = '{"title": "AI Overview", "summary": "Discusses AI model architectures."}'
    input_pdf_text = "Artificial Intelligence has transformed various industries."
    rag_results = ["AI automates tasks.", "Deep learning is a subset of AI."]

    rendered_prompt = renderer.render(user_query, single_shot_prompt_pdf_text, single_shot_prompt_json, input_pdf_text, rag_results)
    print(rendered_prompt)
