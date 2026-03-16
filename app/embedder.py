import os
import time
from dotenv import load_dotenv
load_dotenv()

import json
import time
import hashlib
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from .config import VECTOR_STORE_DIR, EMBEDDING_MODEL

class Embedder:
    def __init__(self):
        self.cache_path = os.path.join(VECTOR_STORE_DIR, "embedding_cache.json")
        self.index_path = os.path.join(VECTOR_STORE_DIR, "faiss_index")
        self._model = None
        self._cache = self._load_cache()

    def _get_model(self):
        if self._model is None:
            self._model = OllamaEmbeddings(
                model=EMBEDDING_MODEL,
                base_url="http://localhost:11434"
            )
        return self._model

    def _load_cache(self) -> Dict[str, List[float]]:
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r") as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(self._cache, f)

    def build_index(self, chunks: List[dict], rebuild: bool = False, dry_run: bool = False):
        if rebuild and os.path.exists(self.index_path):
            import shutil
            shutil.rmtree(self.index_path, ignore_errors=True)
            self._cache = {}
            if os.path.exists(self.cache_path):
                os.remove(self.cache_path)

        documents = []
        texts_to_embed = []
        hashes_to_embed = []

        for chunk in chunks:
            text = chunk["content"]
            metadata = chunk["metadata"]
            thash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            
            if thash not in self._cache:
                texts_to_embed.append(text)
                hashes_to_embed.append(thash)
                
            doc = Document(page_content=text, metadata=metadata)
            doc.metadata["hash"] = thash
            documents.append(doc)

        # Batch embedding with retry
        if texts_to_embed and not dry_run:
            batch_size = 100
            for i in range(0, len(texts_to_embed), batch_size):
                batch_texts = texts_to_embed[i:i+batch_size]
                batch_hashes = hashes_to_embed[i:i+batch_size]
                
                retries = 3
                for attempt in range(retries):
                    try:
                        embeddings = self._get_model().embed_documents(batch_texts)
                        for idx, emb in enumerate(embeddings):
                            self._cache[batch_hashes[idx]] = emb
                        break
                    except Exception as e:
                        if attempt < retries - 1:
                            time.sleep(2 ** attempt)
                        else:
                            print(f"Failed to embed batch: {e}")
            self._save_cache()

        if dry_run:
            return

        embedded_documents = []
        text_embeddings = []
        
        for doc in documents:
            thash = doc.metadata.get("hash")
            if thash in self._cache:
                embedded_documents.append(doc)
                text_embeddings.append((doc.page_content, self._cache[thash]))

        if not text_embeddings:
            return

        if os.path.exists(self.index_path) and not rebuild:
            vector_store = FAISS.load_local(self.index_path, self._get_model(), allow_dangerous_deserialization=True)
            new_store = FAISS.from_embeddings(text_embeddings, self._get_model(), metadatas=[d.metadata for d in embedded_documents])
            vector_store.merge_from(new_store)
        else:
            vector_store = FAISS.from_embeddings(text_embeddings, self._get_model(), metadatas=[d.metadata for d in embedded_documents])

        vector_store.save_local(self.index_path)
