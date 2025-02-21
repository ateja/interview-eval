import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

class VectorInterviewDb:   
    FAISS_INDEX_FILE = "docs/faiss_index.bin"
    FAISS_METADATA_FILE = "docs/chunked_faiss_metadata.xlsx"
    CHUNKED_FILE = "docs/chunked_interview_questions.xlsx"
    CHUNKED_WITH_EMBEDDINGS_FILE = "docs/chunked_with_embeddings.xlsx"
    REQUIRED_FILEDS = {"Level", "Question", "Difficulty", "LeetCode ID", "Question Text"}

    def __init__(self, input_excel, model= None, index_file_path=FAISS_INDEX_FILE):
        self.index_file_path = index_file_path
        self.input_excel=input_excel
        # Load embedding model
        self.model = model if model else SentenceTransformer("all-MiniLM-L6-v2")
        # Initialize reindex_needed based on the model name
        self.reindex_needed = self.model._model_card_text != "all-MiniLM-L6-v2"
    
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,  # Adjust as needed
    chunk_overlap=50  # Ensure some overlap for continuity
    )  

    def validate_excel(self):
        if(self.reindexing_required()):
            return True
        try:
            df = pd.read_excel(self.input_excel)  # Read the Excel file
            return self.REQUIRED_FILEDS.issubset(df.columns)  # Check if both columns exist
        except Exception as e:
            print(f"Error reading the file: {e}")
            return False  # Return False if file cannot be read  

    # Apply chunking
    def chunk_text(self, text):
        chunks = self.text_splitter.split_text(text)
        return chunks if chunks else [text]  # Ensure at least one chunk

    def reindexing_required(self):
        return True if(os.path.exists(self.FAISS_INDEX_FILE) or self.reindex_needed == True) else False
    
    def populate_index(self):
        df = pd.read_excel(self.input_excel)

        chunked_data = []
        for _, row in df.iterrows():
            level = row["Level"]
            question = row["Question"]
            difficulty = row["Difficulty"]
            leetcode_id = row["LeetCode ID"]
            question_text = row["Question Text"]
            
            # Split question into chunks
            chunks = self.chunk_text(question_text)
            
            for chunk in chunks:
                chunked_data.append({"chunk": chunk, "level": level, 
                                    "difficulty": difficulty, "question_summary": question })

        # Convert to DataFrame
        chunked_df = pd.DataFrame(chunked_data)

        # Save the chunked data to a new Excel file
        chunked_df.to_excel(self.CHUNKED_FILE, index=False)
        print(f"Chunking complete! Data saved to {self.CHUNKED_FILE}")

        # Convert each chunk to an embedding
        chunked_df["embedding"] = chunked_df["chunk"].apply(lambda x: self.model.encode(x).tolist())

        # Save with embeddings
        chunked_df.to_excel(self.CHUNKED_WITH_EMBEDDINGS_FILE, index=False)
        print(f"Embeddings saved to {self.CHUNKED_WITH_EMBEDDINGS_FILE}")

        # Load the Excel file again
        df = pd.read_excel(self.CHUNKED_WITH_EMBEDDINGS_FILE)

        # Ensure embeddings are stored as lists
        df["embedding"] = df["embedding"].apply(lambda x: np.array(eval(x), dtype=np.float32))

        # Convert embeddings into a NumPy array
        embeddings = np.vstack(df["embedding"].values)

        print("Loaded", len(embeddings), "embeddings of dimension", embeddings.shape[1])

        # Get embedding dimensions
        dimension = embeddings.shape[1]  # Should match the embedding size (e.g., 384 for MiniLM)

        # Create a FAISS index
        index = faiss.IndexFlatL2(dimension)  # L2 (Euclidean) distance index

        # Add embeddings to the index
        index.add(embeddings)

        # Save the FAISS index
        faiss.write_index(index, self.FAISS_INDEX_FILE)
        print(f"FAISS index saved to {self.FAISS_INDEX_FILE}")

        self.index = index
        # Save metadata (chunked text + level) to keep reference to FAISS results
        df[["chunk", "level", "difficulty", "question_summary"]].to_excel(self.FAISS_METADATA_FILE, index=False)
        print(f"FAISS metadata saved to {self.FAISS_METADATA_FILE}")

    def search_faiss(self, query, top_k=5):
        df = self.load_chunked_data()
        query_embedding = self.encode_query(query)
        # Load FAISS index if not in memory
        if not hasattr(self, "index"):
            if self.reindexing_required():
                self.index = faiss.read_index(self.FAISS_INDEX_FILE)
            else:
                print("FAISS index does not exist. Please run `populate_index()` first.")
                return None        
        distances, indices = self.index.search(query_embedding, top_k)

            # Retrieve matching chunks
        results = df.iloc[indices[0]]
        return results
    
    # Encode the query using the same embedding model
    def encode_query(self, query):
        query_embedding = self.model.encode(query).astype(np.float32)
        return np.array([query_embedding])

    # Load the chunked interview questions
    def load_chunked_data(self):
        df = pd.read_excel(self.CHUNKED_WITH_EMBEDDINGS_FILE)
        df["embedding"] = df["embedding"].apply(lambda x: np.array(eval(x), dtype=np.float32))
        print(f"Loaded {len(df)} chunked interview questions.")
        return df

if __name__ == "__main__":
    vdb = VectorInterviewDb("docs/interview_questions.xlsx")
    vdb.populate_index()
    results = vdb.search_faiss("find list related questions")
    print(results[["chunk", "level"]])


