import logging
from typing import Dict, List, Set, Optional

logger = logging.getLogger(__name__)

class SearchEngine:
    """
    Provides search functionality on top of the inverted index.

    Required Features (from COMP3011 brief):
    - print <word>: display index entry
    - find <words>: AND-search across pages
    - case-insensitive lookup
    - supports multi-word queries
    """

    def __init__(self, index: Dict):
        self.index = index

    # ----------------------------------------------------------
    # Normalise words
    # ----------------------------------------------------------

    def normalize(self, word: str) -> str:
        return word.lower().strip()

    # ----------------------------------------------------------
    # PRINT command
    # ----------------------------------------------------------

    def search_print(self, word: str) -> Optional[Dict]:
        """
        Returns index entry for a single word.
        Handles missing words & empty input.
        """
        if not word.strip():
            logger.warning("Empty word passed to print().")
            return None

        word = self.normalize(word)

        if word not in self.index:
            logger.info(f"Word '{word}' not found in index.")
            return None

        return self.index[word]

    # ----------------------------------------------------------
    # FIND command (AND-search)
    # ----------------------------------------------------------

    def search_find(self, words: List[str]) -> List[str]:
        """
        Returns list of pages that contain ALL given words (AND-search).
        Fulfills brief requirement for multiword queries.
        """

        # Filter out blank words
        clean = [self.normalize(w) for w in words if w.strip()]

        if not clean:
            logger.warning("Empty find query received.")
            return []

        # Check if any word appears in the index
        for w in clean:
            if w not in self.index:
                logger.info(f"'{w}' not in index → no pages match.")
                return []

        # Start with the set of pages for the first word
        result_pages: Set[str] = set(self.index[clean[0]].keys())

        # Intersect with all other word page-sets
        for w in clean[1:]:
            pages = set(self.index[w].keys())
            result_pages = result_pages.intersection(pages)

            if not result_pages:
                return []

        return sorted(result_pages)