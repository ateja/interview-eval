import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from vectordb import VectorInterviewDb

class ModelEvaluation:
    def __init__(self, model_name, input_excel="docs/interview_questions.xlsx", top_k=5):
        """
        Initialize the evaluation with a specific embedding model.
        :param model_name: Name of the sentence-transformers model
        :param input_excel: Path to the question database
        :param top_k: Number of results to retrieve
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.top_k = top_k
        
        # Initialize FAISS index with the given model
        self.vdb = VectorInterviewDb(input_excel, model=self.model)
        self.vdb.populate_index()
        
        # Load ideal results for evaluation
        self.query_ideal_results = {
            "Find an easy problem related to hash tables.": ["Two Sum", "LRU Cache", "Minimum Window Substring"],
            "Give me a graph problem that uses DFS.": ["Flood Fill", "Lowest Common Ancestor of a Binary Tree", "Course Schedule"],
            "I need a linked list problem that involves recursion.": ["Merge Two Sorted Lists", "Add Two Numbers", "Merge k Sorted Lists"],
            "What is a good problem on binary search?": ["Binary Search"],
            "Suggest a problem related to topological sorting.": ["3Sum", "Course Schedule", "Alien Dictionary"],
            "Find a problem that involves implementing a cache.": [],
            "What is a good example of a two-pointer technique problem?": [],
            "Give me a problem that is classified under dynamic programming.": ["Regular Expression Matching"],
            "Show me a problem where heap data structure is used.": ["Kth Largest Element in an Array", "Find Median from Data Stream", "Merge k Sorted Lists"],
            "I want a problem related to designing a data structure.": ["LRU Cache", "Find Median from Data Stream", "Implement Trie (Prefix Tree)"]
        }

    def compute_metrics(self, retrieved, ideal):
        """Compute precision, recall, and F1 score metrics."""
        ideal_set = set(ideal)
        retrieved_set = set(retrieved)

        precision = len(retrieved_set & ideal_set) / len(retrieved_set) if retrieved_set else 0
        recall = len(retrieved_set & ideal_set) / len(ideal_set) if ideal_set else 0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return precision, recall, f1_score

    def evaluate(self):
        """Evaluate the model's performance on the stored queries."""
        evaluation_results = []
        
        for query, ideal_results in self.query_ideal_results.items():
            results = self.vdb.search_faiss(query, top_k=self.top_k)
            
            if results is not None and not results.empty:
                retrieved_questions = results["question_summary"].tolist()
            else:
                retrieved_questions = []

            precision, recall, f1_score = self.compute_metrics(retrieved_questions, ideal_results)

            evaluation_results.append({
                "Model": self.model_name,
                "Query": query,
                "Retrieved Questions": ", ".join(retrieved_questions),
                "Ideal Questions": ", ".join(ideal_results),
                "Precision": precision,
                "Recall": recall,
                "F1 Score": f1_score,
                "Model Name": self.model_name
            })

        return pd.DataFrame(evaluation_results)

if __name__ == "__main__":
    # Test with different models
    models_to_test = ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "multi-qa-mpnet-base-dot-v1"]
    
    all_results = []
    f1_scores = {}
    for model_name in models_to_test:
        evaluator = ModelEvaluation(model_name)
        model_results = evaluator.evaluate()
        all_results.append(model_results)
        
        # Compute average F1 score for the model
        avg_f1 = model_results["F1 Score"].mean()
        f1_scores[model_name] = avg_f1
    
    # Combine all results into a single DataFrame
    final_results = pd.concat(all_results, ignore_index=True)
    
    # Save results to an Excel file
    output_file = "docs/model_comparison_results.xlsx"
    final_results.to_excel(output_file, index=False)
    
    print(f"Evaluation results saved to {output_file}")
    
    # Print the F1 scores for each model
    for model, score in f1_scores.items():
        print(f"Model: {model}, Average F1 Score: {score:.4f}")
