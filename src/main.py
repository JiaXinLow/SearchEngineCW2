import logging
import os

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
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
console.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console)


# ----------------------------------------------------------
# HELP COMMAND
# ----------------------------------------------------------
def command_help():
    print("\nAvailable Commands:")
    print("  build                Crawl website, build index, save to file")
    print("  load                 Load index from data/index.json")
    print("  print <word>         Show index entry for a word")
    print("  find <w1 w2 ...>     AND-search, ranked using TF-IDF")
    print("  help                 Show this help menu")
    print("  exit                 Quit the application")
    print("\nExamples:")
    print("  print life")
    print("  find good friends\n")


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

    crawler = Crawler()
    pages = crawler.run()

    if not pages:
        logger.error("Crawler returned no pages. Aborting build.")
        return None

    indexer = Indexer()
    indexer.build(pages)

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
    print <word>: Show the inverted index entry for a word.
    """
    if indexer is None:
        print("Please run 'load' first.")
        return

    engine = SearchEngine(indexer.index)
    entry = engine.search_print(word)

    if entry is None:
        print(f"No entry for '{word}'")
    else:
        print(f"\nWORD: {word}")
        print("-" * 40)
        for page, stats in entry.items():
            print(f"Page: {page}")
            print(f"  Frequency: {stats['frequency']}")
            print(f"  Positions: {stats['positions']}")
            print("-" * 40)
        print()


def command_find(indexer: Indexer, query: str):
    """
    find <word1 word2 ...>:
    Return all pages containing ALL query words.
    Results are ranked with TF-IDF.
    """
    if indexer is None:
        print("Please run 'load' first.")
        return

    engine = SearchEngine(indexer.index)
    words = query.split()
    ranked_pages = engine.search_find(words)

    if not ranked_pages:
        print("No matching pages found.")
    else:
        print("\nPages ranked by TF-IDF relevance:")
        print("-" * 40)
        for rank, (page, score) in enumerate(ranked_pages, start=1):
            print(f"{rank}. {page} (score = {score:.4f})")
        print("-" * 40)
        print()


# ----------------------------------------------------------
# CLI Loop
# ----------------------------------------------------------
def main():
    indexer = None  # loaded index stored here

    logger.info("Search Engine CLI ready.")
    logger.info("Type 'help' for available commands.")

    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        # HELP
        if cmd == "help":
            command_help()

        # CORE COMMANDS
        elif cmd == "build":
            indexer = command_build()

        elif cmd == "load":
            indexer = command_load()

        elif cmd == "exit":
            logger.info("Exiting...")
            break

        # PRINT
        elif cmd.startswith("print"):
            parts = cmd.split(maxsplit=1)

            if indexer is None:
                print("Please run 'load' first.")
                continue

            if len(parts) == 1 or not parts[1].strip():
                print("Usage: print <word>")
                continue

            word = parts[1].strip()
            command_print(indexer, word)

        # FIND
        elif cmd.startswith("find"):
            parts = cmd.split(maxsplit=1)

            if indexer is None:
                print("Please run 'load' first.")
                continue

            if len(parts) == 1 or not parts[1].strip():
                print("Usage: find <word1 word2 ...>")
                continue

            query = parts[1].strip()
            command_find(indexer, query)

        # UNKNOWN COMMAND
        else:
            print(f"Unknown command: '{cmd}'")
            print("Type 'help' for a list of valid commands.\n")


if __name__ == "__main__":
    main()