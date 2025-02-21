import json
import numpy as np
import pandas as pd
from vectordb import VectorInterviewDb

# Load FAISS index and question database
vdb = VectorInterviewDb("docs/interview_questions.xlsx")
vdb.populate_index()

# Load stored queries and their ideal results
query_ideal_results = {
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

# Load the database of questions
with open("docs/questions_db.json", "r") as file:
    data = json.load(file)

# Extract questions into a DataFrame
question_list = []
for role in data.values():
    for q in role:
        question_list.append({"question": q["question"]})

df_questions = pd.DataFrame(question_list)

# Function to compute precision and recall
def compute_metrics(retrieved, ideal):
    ideal_set = set(ideal)
    retrieved_set = set(retrieved)

    precision = len(retrieved_set & ideal_set) / len(retrieved_set) if retrieved_set else 0
    recall = len(retrieved_set & ideal_set) / len(ideal_set) if ideal_set else 0

    return precision, recall

# Number of results to retrieve from FAISS
K = 5
evaluation_results = []

# Process each query using search_faiss
for query, ideal_results in query_ideal_results.items():
    results = vdb.search_faiss(query, top_k=K)

    if results is not None and not results.empty:
        retrieved_questions = results["question_summary"].tolist()
    else:
        retrieved_questions = []

    precision, recall = compute_metrics(retrieved_questions, ideal_results)

    evaluation_results.append({
        "Query": query,
        "Retrieved Questions": retrieved_questions,
        "Ideal Questions": ideal_results,
        "Precision": precision,
        "Recall": recall
    })

# Convert results to DataFrame and print
df_results = pd.DataFrame(evaluation_results)
print(df_results.to_string(index=False))
