import logging
from typing import Optional, List, Dict, Any
from langchain_ollama import ChatOllama

from .config import LLM_MODEL, LLM_TEMPERATURE, MAX_TOKENS
from .retriever import Retriever, IndexNotReadyError
from .prompt import PROMPT

class Pipeline:
    def __init__(self):
        self.retriever = Retriever()
        self.llm = ChatOllama(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            num_predict=MAX_TOKENS
        )

    def query(self, user_question: str, chat_history: Optional[list] = None, domain_filter: Optional[list] = None) -> Dict[str, Any]:
        try:
            chunks = self.retriever.retrieve(user_question, domain_filter=domain_filter)
        except IndexNotReadyError as e:
            return {
                "answer": "FAISS index not found. Please run ingest.py to build the knowledge base.",
                "sources": [],
                "domain_hits": {}
            }
        except Exception as e:
            logging.error(f"Retrieve error: {e}")
            return {
                "answer": f"An error occurred while retrieving information: {e}",
                "sources": [],
                "domain_hits": {}
            }

        domain_hits = {}
        for c in chunks:
            domain = c["domain"]
            domain_hits[domain] = domain_hits.get(domain, 0) + 1

        if not chunks:
            return {
                "answer": "I don't have enough information in the provided documents to answer that. Try running the ingestion script to add more documentation.",
                "sources": [],
                "domain_hits": domain_hits
            }

        retrieved_texts = []
        for c in chunks:
            title = c["source_url"] if c["source_url"] else c["source_file"]
            text_block = f"Domain: {c['domain']} | Source: {title} | Chunk ID: {c['chunk_id']}\nContent: {c['text']}"
            retrieved_texts.append(text_block)

        context_str = "\n\n".join(retrieved_texts)
        history_str = ""
        if chat_history:
            for msg in chat_history:
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_str += f"{role}: {msg.get('content')}\n"

        prompt_text = PROMPT.format(
            chat_history=history_str,
            retrieved_chunks=context_str,
            user_question=user_question
        )

        try:
            stream = self.llm.stream(prompt_text)
            return {
                "answer": stream,
                "sources": chunks,
                "domain_hits": domain_hits
            }
        except Exception as e:
            logging.error(f"LLM API error: {e}")
            return {
                "answer": f"An API error occurred while generating the answer: {e}",
                "sources": chunks,
                "domain_hits": domain_hits
            }
