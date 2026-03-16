import os
import hashlib
import logging
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from urllib.parse import urlparse

# Define domains for mapping urls/files to specific categories
DOMAINS = ["kubernetes", "docker", "cicd", "terraform", "helm", "gitops"]

def get_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def extract_domain(source: str):
    source_lower = source.lower()
    for d in DOMAINS:
        if d in source_lower:
            return d
    return "other"

def fetch_web(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strip out unwanted tags
        for script_or_style in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            script_or_style.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None

def scrape_and_load(urls, local_dir, local_only=False):
    results = []
    seen_hashes = set()
    
    # Process local files
    if os.path.exists(local_dir):
        for root, _, files in os.walk(local_dir):
            for file in files:
                filepath = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                try:
                    text = ""
                    if ext in ['.txt', '.md']:
                        loader = TextLoader(filepath)
                        docs = loader.load()
                        text = "\n".join([d.page_content for d in docs])
                    elif ext == '.pdf':
                        loader = PyPDFLoader(filepath)
                        docs = loader.load()
                        text = "\n".join([d.page_content for d in docs])
                    
                    if text:
                        thash = get_hash(text)
                        if thash not in seen_hashes:
                            seen_hashes.add(thash)
                            results.append({
                                "content": text,
                                "source_url": "",
                                "source_file": file,
                                "domain": extract_domain(file)
                            })
                except Exception as e:
                    logging.error(f"Failed to process {filepath}: {e}")

    # Process web URLs
    if not local_only:
        for url in urls:
            text = fetch_web(url)
            if text:
                thash = get_hash(text)
                if thash not in seen_hashes:
                    seen_hashes.add(thash)
                    results.append({
                        "content": text,
                        "source_url": url,
                        "source_file": "",
                        "domain": extract_domain(url)
                    })

    return results
