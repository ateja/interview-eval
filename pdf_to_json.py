from pypdf import PdfReader
import glob
import json

class PDFTextExtractor:
    def __init__(self, pdf_path):
        """Initializes the extractor with a given PDF file path."""
        self.pdf_path = pdf_path
        self.text = self._extract_text()
    
    def _extract_text(self):
        """Extracts text from the PDF file."""
        try:
            reader = PdfReader(self.pdf_path)
            return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        except Exception as e:
            return f"Error extracting text from PDF: {e}"
    
    def extract_text_between(self, start_str, end_str):
        """Extracts text between the second occurrence of start_str and the next occurrence of end_str."""
        first_idx = self.text.find(start_str)
        if first_idx == -1:
            return None  # start_str not found
        
        second_idx = self.text.find(start_str, first_idx + len(start_str))
        if second_idx == -1:
            return None  # No second occurrence of start_str
        
        start_idx = second_idx + len(start_str)
        end_idx = self.text.find(end_str, start_idx)
        if end_idx == -1:
            return None  # end_str not found
        
        return self.text[start_idx:end_idx].strip()
    
    def get_json_feedback(self):
        """Extracts interview feedback sections and returns them as JSON."""
        sections = ["1st Interview", "2nd Interview", "3rd Interview", "4th Interview", "5th Interview"]
        end_section = "Personality Traits"
        data = []
        
        for i in range(len(sections)):
            current_section = sections[i]
            next_section = sections[i + 1] if i < len(sections) - 1 else end_section
            content = self.extract_text_between(current_section, next_section)
            data.append({"interview": sections[i], "content": content})
        
        return json.dumps(data, indent=4)

# Example Usage:
# extractor = PDFTextExtractor("path/to/pdf.pdf")
# feedback_json = extractor.get_json_feedback()
# print(feedback_json)


if __name__ == "__main__":
    for file_path in glob.glob("docs/training data/candidate[1]*.pdf"):  # Matches candidate1.pdf, candidate2.pdf, etc.
    #     print(file_path) # Prints the filename (e.g., candidate1.pdf)
        extractor = PDFTextExtractor(file_path)
        feedback_json = extractor.get_json_feedback()
        print(feedback_json)

    # sections = ["1st Interview", "2nd Interview", "3rd Interview", "4th Interview", "5th Interview"]
    # end_section = "Personality Traits"
    # data = []
    # # for file_path in glob.glob("candidate[1-9]*.pdf"):  # Matches candidate1.pdf, candidate2.pdf, etc.
    # for file_path in glob.glob("docs/training data/candidate[1]*.pdf"):  # Matches candidate1.pdf, candidate2.pdf, etc.
    #     print(file_path) # Prints the filename (e.g., candidate1.pdf)
    #     pdf_path = os.path.join(".", file_path)
    #     text = extract_text_from_pdf(pdf_path)
    #     print(f"Extracted text from {pdf_path}")
    #     # Extract content between sections with automatic font size detection
    #     for i in range(len(sections)):
    #         current_section = sections[i]
    #         next_section = sections[i + 1] if i < len(sections) - 1 else end_section
    #         content = extract_text_between(text, current_section, next_section)
    #         data.append({"interview":sections[i], "content":content})

    #     json_data = json.dumps(data, indent=4)
    #     print(json_data)
