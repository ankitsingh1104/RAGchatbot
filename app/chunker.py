import re
import uuid
import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import CHUNK_SIZE, CHUNK_OVERLAP

def clean(text: str) -> str:
    # remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # remove non-ASCII
    text = text.encode("ascii", "ignore").decode()
    
    # remove lines under 80 characters (but keep some structure)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if len(line.strip()) >= 80:
            # collapse whitespace per line
            line = re.sub(r'\s+', ' ', line).strip()
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines)

def chunk(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=['\n\n', '\n', '. ', ' ', '']
    )
    
    chunks = []
    fetch_date = datetime.datetime.now().isoformat()
    
    for doc in documents:
        cleaned_text = clean(doc["content"])
        if not cleaned_text:
            continue
            
        splits = splitter.split_text(cleaned_text)
        
        for t in splits:
            if len(t.strip()) < 80:
                continue
            
            # Filter out purely code chunks: simplistic check - if lots of syntax brackets and no regular text
            if '{' in t and '}' in t and not re.search(r'[A-Za-z]{4,}', t):
                continue
                
            chunks.append({
                "content": t,
                "metadata": {
                    "source_url": doc["source_url"],
                    "source_file": doc["source_file"],
                    "domain": doc["domain"],
                    "topic": doc["domain"], # default topic to domain
                    "chunk_id": str(uuid.uuid4()),
                    "fetch_date": fetch_date
                }
            })
            
    return chunks
