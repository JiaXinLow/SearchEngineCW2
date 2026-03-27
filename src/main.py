import logging
import os
import sys

from crawler import Crawler
from indexer import Indexer
from search import SearchEngine

INDEX_PATH = "data/index.json"

# ----------------------------------------------------------
# Logging Setup
# ----------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
)
console.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console)

# ----------------------------------------------------------
# CLI Command Implementations
# ----------------------------------------------------------
def command_build():
    """
    build: crawl → index → save
    Required by the coursework brief:
    - crawl the website
    - build the inverted index
    - save the result as a single file
    """
    logger.info("Starting BUILD command...")

    # 1. Crawl
    crawler = Crawler()
    pages = crawler.run()

    if not pages:
        logger.error("Crawler returned no pages. Aborting build.")
        return None

    # 2. Index
    indexer = Indexer()
    indexer.build(pages)

    # 3. Save to data/
    os.makedirs("data", exist_ok=True)
    indexer.save(INDEX_PATH)

    logger.info(f"BUILD complete. Index saved to {INDEX_PATH}")
    return indexer

def command_load():
    """
    load: loads the saved index file.
    Required by the brief:
    - load index from a single file
    - handle missing file gracefully
    """
    logger.info("Starting LOAD command...")

    if not os.path.exists(INDEX_PATH):
        logger.error(f"Index file not found at {INDEX_PATH}.")
        logger.error("Please run 'build' first.")
        return None

    indexer = Indexer()
    indexer.load(INDEX_PATH)

    logger.info("LOAD complete — index is ready.")
    return indexer

def command_print(indexer: Indexer, word: str):
    """
    print <word>:
    Show the inverted index entry for a word.
    Required by the brief.
    """
    if indexer is None:
        print("Please run 'load' first.")
        return

    engine = SearchEngine(indexer.index)
    entry = engine.search_print(word)

    if entry is None:
        print(f"No entry for '{word}'")
    else:
        print(f"Word: {word}")
        for page, stats in entry.items():
            print(f" - Page: {page}")
            print(f"   Frequency: {stats['frequency']}")
            print(f"   Positions: {stats['positions']}")

def command_find(indexer: Indexer, query: str):
    """
    find <word1 word2 ...>:
    Return all pages containing ALL query words.
    Required by the brief.
    """
    if indexer is None:
        print("Please run 'load' first.")
        return

    engine = SearchEngine(indexer.index)
    words = query.split()
    pages = engine.search_find(words)

    if not pages:
        print("No matching pages found.")
    else:
        print("Pages containing ALL words:", pages)

# ----------------------------------------------------------
# CLI Loop
# ----------------------------------------------------------
def main():
    indexer = None  # loaded index stored here

    logger.info("Search Engine CLI ready.")
    logger.info("Commands: build, load, print <word>, find <words>, exit")

    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        # No input
        if not cmd:
            continue

        # Dispatch commands
        if cmd == "build":
            indexer = command_build()

        elif cmd == "load":
            indexer = command_load()

        # -------- PRINT COMMAND --------
        elif cmd.startswith("print"):
            if indexer is None:
                print("Please run 'load' first.")
                continue

            parts = cmd.split(maxsplit=1)

            if len(parts) == 1 or not parts[1].strip():
                print("Usage: print <word>")
                continue

            word = parts[1].strip()
            command_print(indexer, word)

        # -------- FIND COMMAND --------
        elif cmd.startswith("find"):
            if indexer is None:
                print("Please run 'load' first.")
                continue

            parts = cmd.split(maxsplit=1)

            if len(parts) == 1 or not parts[1].strip():
                print("Usage: find <word1 word2 ...>")
                continue

            query = parts[1].strip()
            command_find(indexer, query)

        elif cmd == "exit":
            logger.info("Exiting...")
            break

        else:
            print("Unknown command. Options: build, load, print, find, exit")

if __name__ == "__main__":
    main()