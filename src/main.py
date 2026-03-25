import logging
import os
import sys

from crawler import Crawler
from indexer import Indexer

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
    Required by coursework brief:
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
        return

    # 2. Index
    indexer = Indexer()
    indexer.build(pages)

    # 3. Save
    os.makedirs("data", exist_ok=True)
    indexer.save(INDEX_PATH)

    logger.info(f"BUILD complete. Index saved to {INDEX_PATH}")


def command_load():
    """
    load: loads the saved index file
    Required by coursework brief:
    - load index from file
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


# ----------------------------------------------------------
# CLI Loop
# ----------------------------------------------------------

def main():
    logger.info("Search Engine CLI ready.")
    logger.info("Commands: build, load, exit")

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if cmd == "build":
            command_build()

        elif cmd == "load":
            indexer = command_load()
            # later: store globally if needed for print/find

        elif cmd == "exit":
            logger.info("Exiting...")
            break

        else:
            print("Unknown command. Options: build, load, exit")


if __name__ == "__main__":
    main()