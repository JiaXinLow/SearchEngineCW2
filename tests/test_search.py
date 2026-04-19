import unittest
import sys, os

# ensure src/ is on path BEFORE imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from search import SearchEngine


class TestSearchEngine(unittest.TestCase):

    def setUp(self):
        """
        Create a small sample inverted index for testing.
        Format matches indexer.py output.
        This dataset is intentionally simple so TF‑IDF
        ranking can be tested deterministically.
        """
        self.sample_index = {
            "hello": {
                "page1": {"frequency": 2, "positions": [0, 5]},
                "page2": {"frequency": 1, "positions": [3]}
            },
            "world": {
                "page1": {"frequency": 1, "positions": [1]},
                "page3": {"frequency": 1, "positions": [7]}
            }
        }

        self.engine = SearchEngine(self.sample_index)

    # ------------------------------------------------------
    # PRINT Tests
    # ------------------------------------------------------
    def test_print_existing_word(self):
        entry = self.engine.search_print("hello")
        self.assertIsNotNone(entry)
        self.assertIn("page1", entry)
        self.assertEqual(entry["page1"]["frequency"], 2)

    def test_print_missing_word(self):
        entry = self.engine.search_print("missingword")
        self.assertIsNone(entry)

    def test_print_empty_string(self):
        entry = self.engine.search_print("")
        self.assertIsNone(entry)

    # ------------------------------------------------------
    # FIND Tests (AND-search WITHOUT ranking effects)
    # ------------------------------------------------------
    def test_find_single_word(self):
        # hello appears in page1 (TF=2) and page2 (TF=1)
        # Both should be returned — ranking decides order
        results = self.engine.search_find(["hello"])
        pages = [p for p, _ in results]
        self.assertEqual(sorted(pages), ["page1", "page2"])

    def test_find_multiple_words_and_search(self):
        # Only page1 has BOTH hello + world
        results = self.engine.search_find(["hello", "world"])
        pages = [p for p, _ in results]
        self.assertEqual(pages, ["page1"])

    def test_find_no_overlap(self):
        results = self.engine.search_find(["hello", "nonexistent"])
        self.assertEqual(results, [])

    def test_find_empty_query(self):
        results = self.engine.search_find([])
        self.assertEqual(results, [])

    # ------------------------------------------------------
    # Case-insensitivity
    # ------------------------------------------------------
    def test_case_insensitive(self):
        results = self.engine.search_find(["HeLLo"])
        pages = [p for p, _ in results]
        self.assertEqual(sorted(pages), ["page1", "page2"])

    # ------------------------------------------------------
    # TF-IDF Ranking Tests
    # ------------------------------------------------------
    def test_tfidf_ranking_single_word(self):
        """
        For the word 'hello':
        page1: TF=2
        page2: TF=1

        IDF is identical for both pages, so ranking must be:
        page1 first, then page2.
        """
        results = self.engine.search_find(["hello"])
        pages = [p for p, _ in results]
        self.assertEqual(pages, ["page1", "page2"])

    def test_tfidf_ranking_multi_word(self):
        """
        hello (page1:2, page2:1), world (page1:1, page3:1)
        AND search on: ["hello", "world"]

        Only page1 contains BOTH.
        Ranking should return only page1.
        """
        results = self.engine.search_find(["hello", "world"])
        self.assertEqual(results[0][0], "page1")

    def test_tfidf_ranking_prefers_higher_score(self):
        """
        TF-IDF ranking should prefer higher TF when IDF > 0.
        Here, 'hello' appears in 2 out of 3 documents.
        """
        modified_index = {
            "hello": {
                "page1": {"frequency": 3, "positions": [0, 5, 6]},
                "page2": {"frequency": 1, "positions": [3]}, 
            },
            "other": {
                "page3": {"frequency": 2, "positions": [1, 2]}
            }
        }
        engine = SearchEngine(modified_index)

        results = engine.search_find(["hello"])
        self.assertEqual(results[0][0], "page1")
        self.assertEqual(len(results), 2)

if __name__ == "__main__":
    unittest.main()