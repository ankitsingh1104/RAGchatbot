# importing os library to interact with environment variables and file paths
import os

# importing typing utilities to define list types for better readability
from typing import List

# importing a fake embedding model from sentence transformers
from sentence_transformers import SentenceTransformer

# importing FAISS for vector similarity search
import faiss

# importing numpy for numerical operations and vector handling
import numpy as np

# importing a huggingface pipeline to simulate an LLM
from transformers import pipeline


# defining a class that represents a simple RAG system
class SimpleRAGSystem:

    # constructor method to initialize models and storage
    def __init__(self):

        # loading an embedding model used to convert text into vectors
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        # initializing an empty list to store original documents
        self.documents = []

        # initializing the FAISS vector index as None before building it
        self.index = None

        # loading a text generation model to simulate LLM responses
        self.generator = pipeline("text-generation", model="gpt2")


    # method to add documents to the RAG knowledge base
    def add_documents(self, docs: List[str]):

        # extending the internal document list with new documents
        self.documents.extend(docs)


    # method to build the vector index from stored documents
    def build_index(self):

        # converting all stored documents into embeddings
        embeddings = self.embedding_model.encode(self.documents)

        # converting embeddings to numpy array format
        embeddings = np.array(embeddings).astype("float32")

        # getting the dimension of embeddings
        dimension = embeddings.shape[1]

        # creating a FAISS index using L2 distance
        self.index = faiss.IndexFlatL2(dimension)

        # adding embeddings into the FAISS vector database
        self.index.add(embeddings)


    # method to retrieve relevant documents for a query
    def retrieve(self, query: str, top_k: int = 3):

        # converting the query into embedding vector
        query_vector = self.embedding_model.encode([query])

        # converting query vector to numpy float32 format
        query_vector = np.array(query_vector).astype("float32")

        # performing similarity search in FAISS
        distances, indices = self.index.search(query_vector, top_k)

        # retrieving corresponding documents using returned indices
        results = [self.documents[i] for i in indices[0]]

        # returning the retrieved documents
        return results


    # method to generate final answer using retrieved context
    def generate_answer(self, query: str):

        # retrieving top relevant documents for the query
        retrieved_docs = self.retrieve(query)

        # combining retrieved documents into a single context string
        context = " ".join(retrieved_docs)

        # constructing the prompt using context and user query
        prompt = f"Context: {context}\nQuestion: {query}\nAnswer:"

        # generating answer from the language model
        result = self.generator(prompt, max_length=100, num_return_sequences=1)

        # extracting generated text from result dictionary
        answer = result[0]["generated_text"]

        # returning the generated answer
        return answer


# creating an instance of the RAG system
rag = SimpleRAGSystem()

# defining some example documents to simulate a knowledge base
sample_docs = [
    "Retrieval Augmented Generation combines retrieval systems with language models.",
    "Vector databases store embeddings for fast similarity search.",
    "Embeddings convert text into high dimensional numerical vectors.",
    "Large language models generate responses based on prompts."
]

# adding documents to the RAG system
rag.add_documents(sample_docs)

# building the FAISS vector index from the documents
rag.build_index()

# defining a user query for testing the system
query = "What is retrieval augmented generation?"

# generating an answer using the RAG pipeline
answer = rag.generate_answer(query)

# printing the generated answer to the console
print(answer)