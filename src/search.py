import logging
import math
from typing import Dict, List, Set, Optional, Tuple

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SearchEngine:
    """
    Provides search functionality on top of the inverted index.

    Features:
    - print <word>  : display index entry
    - find <words>  : AND-search with TF-IDF ranking
    - case-insensitive lookup
    - multi-word query support
    - TF-IDF scoring exposed for ranked output
    """

    def __init__(self, index: Dict):
        self.index = index
        logger.debug(f"SearchEngine initialized with {len(index)} indexed words.")

        # Pre-calc number of documents for IDF
        self.total_docs = self._count_total_documents()
        logger.debug(f"Total documents detected: {self.total_docs}")

    # ----------------------------------------------------------
    # INTERNAL UTILS
    # ----------------------------------------------------------

    def _count_total_documents(self) -> int:
        """Total number of documents seen in index."""
        pages = set()
        for word_data in self.index.values():
            for page_url in word_data.keys():
                pages.add(page_url)
        return len(pages)

    # ----------------------------------------------------------
    # Normalise words
    # ----------------------------------------------------------

    def normalize(self, word: str) -> str:
        norm = word.lower().strip()
        logger.debug(f"Normalizing search word '{word}' -> '{norm}'")
        return norm

    # ----------------------------------------------------------
    # PRINT command
    # ----------------------------------------------------------

    def search_print(self, word: str) -> Optional[Dict]:
        """
        Returns index entry for a single word.
        Handles missing words & empty input.
        """
        logger.info(f"PRINT query: '{word}'")

        if not word.strip():
            logger.warning("Empty word passed to print().")
            return None

        word = self.normalize(word)

        if word not in self.index:
            logger.info(f"Word '{word}' not found in index.")
            return None

        logger.debug(f"PRINT result for '{word}': {self.index[word]}")
        return self.index[word]

    # ----------------------------------------------------------
    # TF-IDF COMPONENTS
    # ----------------------------------------------------------

    def term_frequency(self, word: str, page: str) -> float:
        """
        TF = frequency of the word in this document.
        """
        freq = self.index[word][page]["frequency"]
        logger.debug(f"TF({word}, {page}) = {freq}")
        return freq

    def inverse_document_frequency(self, word: str) -> float:
        """
        IDF = log(total_docs / docs_with_word)
        Ensures words appearing in fewer documents have higher weight.
        """
        docs_with_word = len(self.index[word].keys())
        if docs_with_word == 0:
            return 0.0

        idf = math.log(self.total_docs / docs_with_word)
        logger.debug(f"IDF({word}) = {idf}")
        return idf

    def tfidf(self, word: str, page: str) -> float:
        """Compute TF-IDF score for a single word on a specific page."""
        tf = self.term_frequency(word, page)
        idf = self.inverse_document_frequency(word)
        score = tf * idf
        logger.debug(f"TF-IDF({word}, {page}) = {score}")
        return score

    # ----------------------------------------------------------
    # FIND command (AND-search + TF-IDF ranking)
    # ----------------------------------------------------------

    def search_find(self, words: List[str]) -> List[Tuple[str, float]]:
        """
        Returns list of pages that contain ALL given words (AND-search),
        ranked by total TF-IDF score.
        """
        logger.info(f"FIND query: {words}")

        # Filter out blank words
        clean = [self.normalize(w) for w in words if w.strip()]

        if not clean:
            logger.warning("Empty find query received.")
            return []

        # Check if all words are known
        for w in clean:
            if w not in self.index:
                logger.info(f"'{w}' not in index → no pages match.")
                return []

        # AND-search → intersection of pages
        result_pages: Set[str] = set(self.index[clean[0]].keys())

        for w in clean[1:]:
            pages = set(self.index[w].keys())
            result_pages = result_pages.intersection(pages)

            if not result_pages:
                logger.info("No pages contained all query words.")
                return []

        # ---------- TF-IDF RANKING ----------
        scored_pages: List[Tuple[str, float]] = []

        for page in result_pages:
            total_score = 0.0
            for w in clean:
                total_score += self.tfidf(w, page)
            scored_pages.append((page, total_score))
            logger.debug(f"Aggregated TF-IDF for page '{page}' = {total_score}")

        # Sort descending by score
        scored_pages.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Ranked FIND result with scores: {scored_pages}")
        return scored_pages