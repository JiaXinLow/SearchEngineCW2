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
    # FIND Tests (AND-search)
    # ------------------------------------------------------
    def test_find_single_word(self):
        pages = self.engine.search_find(["hello"])
        self.assertEqual(pages, ["page1", "page2"])

    def test_find_multiple_words_and_search(self):
        # Only page1 has BOTH "hello" and "world"
        pages = self.engine.search_find(["hello", "world"])
        self.assertEqual(pages, ["page1"])

    def test_find_no_overlap(self):
        pages = self.engine.search_find(["hello", "nonexistent"])
        self.assertEqual(pages, [])

    def test_find_empty_query(self):
        pages = self.engine.search_find([])
        self.assertEqual(pages, [])

    # ------------------------------------------------------
    # Case-insensitivity
    # ------------------------------------------------------
    def test_case_insensitive(self):
        pages = self.engine.search_find(["HeLLo"])
        self.assertEqual(pages, ["page1", "page2"])


if __name__ == "__main__":
    unittest.main()