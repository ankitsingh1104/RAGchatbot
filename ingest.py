import os
import sys
import time
import argparse
from app.config import DATA_DOCS_DIR
from app.scraper import scrape_and_load
from app.chunker import chunk
from app.embedder import Embedder

URLS = [
    "https://kubernetes.io/docs/concepts/",
    "https://kubernetes.io/docs/tasks/",
    "https://kubernetes.io/docs/reference/kubectl/cheatsheet/",
    "https://docs.docker.com/get-started/",
    "https://docs.docker.com/engine/reference/builder/",
    "https://docs.docker.com/compose/",
    "https://docs.github.com/en/actions",
    "https://docs.gitlab.com/ee/ci/",
    "https://developer.hashicorp.com/terraform/docs",
    "https://helm.sh/docs/",
    "https://argo-cd.readthedocs.io/en/stable/"
]

def main():
    parser = argparse.ArgumentParser(description="Ingest DevOps documentation into FAISS vector store.")
    parser.add_argument("--domain", type=str, help="Single domain to filter URLs (e.g. kubernetes)")
    parser.add_argument("--rebuild", action="store_true", help="Clear existing index and rebuild from scratch")
    parser.add_argument("--local-only", action="store_true", help="Skip web scraping, only load local files")
    parser.add_argument("--dry-run", action="store_true", help="Do not make any API calls or save index")
    
    args = parser.parse_args()

    start_time = time.time()
    
    urls_to_scrape = URLS
    if args.domain:
        urls_to_scrape = [u for u in URLS if args.domain.lower() in u.lower()]

    print(f"[*] Starting ingestion process...")
    print(f"[*] Local Docs Directory: {DATA_DOCS_DIR}")
    
    os.makedirs(DATA_DOCS_DIR, exist_ok=True)
    
    # 1. Scrape & Load
    print(f"[*] Scraping and loading documents...")
    documents = scrape_and_load(urls_to_scrape, DATA_DOCS_DIR, local_only=args.local_only)
    print(f"    - Loaded {len(documents)} document pages.")

    if not documents:
        print("[-] No documents loaded. Exiting.")
        sys.exit(0)

    # 2. Chunk
    print(f"[*] Chunking documents...")
    chunks = chunk(documents)
    print(f"    - Produced {len(chunks)} chunks.")

    if not chunks:
        print("[-] No valid chunks produced. Exiting.")
        sys.exit(0)

    # 3. Embed & Index
    print(f"[*] Embedding and building index...")
    embedder = Embedder()
    failed = False
    try:
        embedder.build_index(chunks, rebuild=args.rebuild, dry_run=args.dry_run)
    except Exception as e:
        print(f"[-] Embedding failed: {e}")
        failed = True

    duration = time.time() - start_time
    
    print(f"\n[*] Ingestion Summary:")
    print(f"    - Mode: {'Dry Run' if args.dry_run else 'Live'}")
    print(f"    - Rebuild: {args.rebuild}")
    print(f"    - Chunks Processed: {len(chunks)}")
    if failed:
        print(f"    - Status: FAILED")
    print(f"    - Duration: {duration:.2f} seconds")
    print(f"[*] Process complete.\n")

    if failed:
        sys.exit(1)

    if not args.dry_run and len(chunks) < 10:
        print("[-] Error: Fewer than 10 chunks indexed. Something may be wrong.")
        sys.exit(1)

if __name__ == "__main__":
    main()
