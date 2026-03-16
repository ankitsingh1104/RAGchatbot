import os
from typing import Optional, List, Dict
from langchain_community.vectorstores import FAISS
from sentence_transformers import CrossEncoder

from .config import VECTOR_STORE_DIR, TOP_K, SIMILARITY_THRESHOLD, RERANK_TOP_K
from .embedder import Embedder

class IndexNotReadyError(Exception):
    pass

class Retriever:
    def __init__(self):
        self.index_path = os.path.join(VECTOR_STORE_DIR, "faiss_index")
        self._vector_store = None
        self._cross_encoder = None
        self._embedder = None

    def _get_vector_store(self):
        if not os.path.exists(self.index_path):
            raise IndexNotReadyError("FAISS index not found. Please run ingest.py.")
        
        if self._vector_store is None:
            if self._embedder is None:
                self._embedder = Embedder()
            self._vector_store = FAISS.load_local(self.index_path, self._embedder._get_model(), allow_dangerous_deserialization=True)
        return self._vector_store

    def _get_cross_encoder(self):
        if self._cross_encoder is None:
            self._cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        return self._cross_encoder

    def retrieve(self, query: str, top_k: int = TOP_K, domain_filter: Optional[List[str]] = None) -> List[dict]:
        vector_store = self._get_vector_store()
        
        docs_and_scores = vector_store.similarity_search_with_relevance_scores(query, k=top_k * 5)
        
        filtered_results = []
        for doc, score in docs_and_scores:
            if domain_filter and doc.metadata.get("domain") not in domain_filter:
                continue
            if score < SIMILARITY_THRESHOLD:
                pass 
            filtered_results.append(doc)

        if not filtered_results:
            return []

        # Rerank
        cross_encoder = self._get_cross_encoder()
        pairs = [[query, doc.page_content] for doc in filtered_results]
        scores = cross_encoder.predict(pairs)

        for idx, doc in enumerate(filtered_results):
            doc.metadata["rerank_score"] = float(scores[idx])

        # Filter by threshold and rank
        reranked = [doc for doc in filtered_results if doc.metadata["rerank_score"] >= SIMILARITY_THRESHOLD]
        reranked.sort(key=lambda x: x.metadata["rerank_score"], reverse=True)
        
        top_results = reranked[:RERANK_TOP_K]

        results = []
        for doc in top_results:
            results.append({
                "text": doc.page_content,
                "source_url": doc.metadata.get("source_url", ""),
                "source_file": doc.metadata.get("source_file", ""),
                "domain": doc.metadata.get("domain", ""),
                "chunk_id": doc.metadata.get("chunk_id", ""),
                "score": doc.metadata["rerank_score"]
            })
            
        return results
