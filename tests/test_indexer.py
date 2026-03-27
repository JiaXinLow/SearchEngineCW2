import unittest
import sys, os

# ensure src/ is on path BEFORE importing indexer or crawler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from indexer import Indexer
from crawler import PageData, Quote


class TestIndexer(unittest.TestCase):

    # -------------------------------------------------------
    # Test: Normalisation (case-insensitive)
    # -------------------------------------------------------
    def test_normalize(self):
        idx = Indexer()
        self.assertEqual(idx.normalize("Hello"), "hello")
        self.assertEqual(idx.normalize("HeLLo!!"), "hello")
        self.assertEqual(idx.normalize("123"), "123")
        self.assertEqual(idx.normalize("   TEST   "), "test")

    # -------------------------------------------------------
    # Test: Frequency & Position Tracking
    # -------------------------------------------------------
    def test_frequency_and_positions(self):
        idx = Indexer()

        # Simulate PageData with quotes
        page = PageData(
            url="page1",
            quotes=[
                Quote(text="Hello world world", author="Author", tags=[])
            ]
        )

        idx.index_page(page)

        # NORMALIZED words: "hello", "world"
        self.assertIn("hello", idx.index)
        self.assertIn("world", idx.index)

        # Frequency checks
        self.assertEqual(idx.index["hello"]["page1"]["frequency"], 1)
        self.assertEqual(idx.index["world"]["page1"]["frequency"], 2)

        # Position checks
        self.assertEqual(idx.index["hello"]["page1"]["positions"], [0])
        self.assertEqual(idx.index["world"]["page1"]["positions"], [1, 2])

    # -------------------------------------------------------
    # Test: Multi-page indexing (ensures page separation)
    # -------------------------------------------------------
    def test_multi_page_indexing(self):
        idx = Indexer()

        page1 = PageData(
            url="page1",
            quotes=[Quote(text="Hello", author="A", tags=[])]
        )
        page2 = PageData(
            url="page2",
            quotes=[Quote(text="Hello again", author="B", tags=[])]
        )

        idx.index_page(page1)
        idx.index_page(page2)

        self.assertIn("page1", idx.index["hello"])
        self.assertIn("page2", idx.index["hello"])

        self.assertEqual(idx.index["hello"]["page1"]["frequency"], 1)
        self.assertEqual(idx.index["hello"]["page2"]["frequency"], 1)

    # -------------------------------------------------------
    # Test: Edge Case – Empty words are ignored
    # -------------------------------------------------------
    def test_empty_word_ignored(self):
        idx = Indexer()
        idx.add_to_index("", "page1", 5)  # should be ignored

        self.assertNotIn("", idx.index)

    # -------------------------------------------------------
    # Test: save + load round-trip
    # -------------------------------------------------------
    def test_save_and_load(self):
        os.makedirs("data", exist_ok=True)

        idx1 = Indexer()

        page = PageData(
            url="page1",
            quotes=[Quote(text="Test save load", author="A", tags=[])]
        )

        idx1.index_page(page)
        idx1.save("data/test_index.json")

        idx2 = Indexer()
        idx2.load("data/test_index.json")

        self.assertEqual(idx1.index, idx2.index)


if __name__ == "__main__":
    unittest.main()