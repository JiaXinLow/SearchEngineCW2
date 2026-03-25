import json
import logging
import re
from dataclasses import dataclass, asdict
from typing import Dict, List
from pathlib import Path

from crawler import PageData, Quote

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------
# Indexer Class
# ---------------------------------------------------------

class Indexer:
    """
    Builds an inverted index from crawled PageData.

    Structure:
    {
        "word": {
            "page_url": {
                "frequency": int,
                "positions": [int, int, ...]
            }
        }
    }
    """

    def __init__(self):
        self.index: Dict[str, Dict[str, Dict[str, List[int] | int]]] = {}

    # ---------------------------------------------------------
    # Word Normalisation
    # ---------------------------------------------------------

    def normalize(self, word: str) -> str:
        """Lowercase and remove punctuation."""
        word = word.lower()
        word = re.sub(r"[^a-z0-9']", "", word)
        return word

    # ---------------------------------------------------------
    # Add Word Occurrence to Index
    # ---------------------------------------------------------

    def add_to_index(self, word: str, page_url: str, position: int) -> None:
        """Adds a word occurrence to the index."""
        if word == "":
            return

        if word not in self.index:
            self.index[word] = {}

        if page_url not in self.index[word]:
            self.index[word][page_url] = {
                "frequency": 0,
                "positions": []
            }

        self.index[word][page_url]["frequency"] += 1
        self.index[word][page_url]["positions"].append(position)

    # ---------------------------------------------------------
    # Index a Single Page
    # ---------------------------------------------------------

    def index_page(self, page: PageData) -> None:
        """
        Converts PageData into indexed word statistics.
        Tracks word positions.
        """
        logger.info(f"Indexing page: {page.url}")

        position = 0  # absolute position of each word

        # Combine all quote text + metadata into one content string
        for quote in page.quotes:
            text_content = f"{quote.text} {quote.author} {' '.join(quote.tags)}"
            words = text_content.split()

            for w in words:
                norm = self.normalize(w)
                self.add_to_index(norm, page.url, position)
                position += 1

    # ---------------------------------------------------------
    # Build Index Over All Pages
    # ---------------------------------------------------------

    def build(self, pages: List[PageData]) -> None:
        """Builds an index from a list of PageData."""
        for page in pages:
            self.index_page(page)

        logger.info(f"Index built with {len(self.index)} unique words.")

    # ---------------------------------------------------------
    # Save / Load
    # ---------------------------------------------------------

    def save(self, filepath: str) -> None:
        """Saves index to JSON."""
        path = Path(filepath)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=4)
        logger.info(f"Index saved to {filepath}")

    def load(self, filepath: str) -> None:
        """Loads index from JSON."""
        path = Path(filepath)
        with path.open("r", encoding="utf-8") as f:
            self.index = json.load(f)
        logger.info(f"Index loaded from {filepath}")