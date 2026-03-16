# importing random module to simulate embedding generation
import random

# importing math module for vector calculations
import math

# importing typing for type hints
from typing import List, Tuple


# defining a helper function to split long text into chunks
def chunk_text(text: str, chunk_size: int = 50) -> List[str]:
    # splitting the input text into words
    words = text.split()

    # creating an empty list to store chunks
    chunks = []

    # iterating through words in steps of chunk_size
    for i in range(0, len(words), chunk_size):
        # joining a slice of words to form a chunk
        chunk = " ".join(words[i:i + chunk_size])

        # adding chunk to the list
        chunks.append(chunk)

    # returning all generated chunks
    return chunks


# defining a fake embedding function
def fake_embedding(text: str, dim: int = 16) -> List[float]:
    # setting seed based on text hash to make embeddings deterministic
    random.seed(hash(text) % (2**32))

    # generating a random vector of fixed dimension
    return [random.random() for _ in range(dim)]


# defining cosine similarity function
def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    # calculating dot product of vectors
    dot = sum(a * b for a, b in zip(v1, v2))

    # calculating magnitude of vector 1
    mag1 = math.sqrt(sum(a * a for a in v1))

    # calculating magnitude of vector 2
    mag2 = math.sqrt(sum(b * b for b in v2))

    # returning cosine similarity score
    return dot / (mag1 * mag2 + 1e-9)


# defining a retriever class
class Retriever:

    # initializing storage for embeddings and text chunks
    def __init__(self):
        # list to store chunks
        self.text_chunks = []

        # list to store vector embeddings
        self.vectors = []

    # method to add documents
    def add_document(self, text: str):
        # splitting document into smaller chunks
        chunks = chunk_text(text)

        # processing each chunk
        for c in chunks:
            # storing the chunk
            self.text_chunks.append(c)

            # computing embedding
            emb = fake_embedding(c)

            # storing embedding
            self.vectors.append(emb)

    # method to retrieve top-k similar chunks
    def search(self, query: str, k: int = 3) -> List[str]:
        # generating embedding for query
        q_vec = fake_embedding(query)

        # creating a list for similarity scores
        scores = []

        # iterating through stored vectors
        for idx, vec in enumerate(self.vectors):
            # computing similarity with query
            score = cosine_similarity(q_vec, vec)

            # storing score and index
            scores.append((score, idx))

        # sorting results by highest similarity
        scores.sort(reverse=True)

        # selecting top-k results
        best = scores[:k]

        # returning corresponding text chunks
        return [self.text_chunks[i] for _, i in best]


# defining a mock LLM generator
class FakeLLM:

    # method to generate answer
    def generate(self, prompt: str) -> str:
        # returning a simulated response based on prompt
        return f"[LLM RESPONSE]\nBased on context I found:\n{prompt[:200]}...\nThis suggests the query relates to retrieved knowledge."


# defining the RAG pipeline class
class RAGPipeline:

    # initializing retriever and LLM
    def __init__(self):
        # creating retriever instance
        self.retriever = Retriever()

        # creating fake LLM instance
        self.llm = FakeLLM()

    # method to load documents into system
    def ingest(self, docs: List[str]):
        # iterating through each document
        for d in docs:
            # sending document to retriever
            self.retriever.add_document(d)

    # method to answer queries
    def ask(self, query: str) -> str:
        # retrieving relevant chunks
        context = self.retriever.search(query)

        # combining context into prompt
        prompt = "CONTEXT:\n" + "\n".join(context) + f"\n\nQUESTION:\n{query}\n\nANSWER:"

        # generating response from fake LLM
        return self.llm.generate(prompt)


# defining some example documents
documents = [
    "RAG systems combine information retrieval with generative AI to produce grounded answers.",
    "Vector embeddings allow similarity search between queries and stored knowledge.",
    "Large language models generate human-like text responses using deep neural networks."
]


# creating RAG pipeline instance
rag = RAGPipeline()

# ingesting documents into the system
rag.ingest(documents)

# defining a user query
user_query = "How do RAG models use retrieval?"

# generating response
response = rag.ask(user_query)

# printing the result
print(response)