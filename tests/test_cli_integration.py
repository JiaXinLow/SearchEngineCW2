import unittest
import sys, os

# ensure src/ is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from indexer import Indexer
from search import SearchEngine
from crawler import PageData, Quote


class TestCLIIntegration(unittest.TestCase):
    """
    Integration test covering the logical CLI workflow:
    index build → search (find)
    This ensures multiple components work together correctly.
    """

    def test_build_load_find_flow(self):
        # Simulate crawled pages (no network access)
        pages = [
            PageData(
                url="page1",
                quotes=[Quote(text="Hello world", author="A", tags=[])]
            ),
            PageData(
                url="page2",
                quotes=[Quote(text="Hello again", author="B", tags=[])]
            )
        ]

        # Build index
        indexer = Indexer()
        indexer.build(pages)

        # Use search engine on built index
        engine = SearchEngine(indexer.index)

        # Perform find command (AND-search)
        results = engine.search_find(["hello"])

        pages_found = [page for page, _ in results]
        self.assertEqual(set(pages_found), {"page1", "page2"})


if __name__ == "__main__":
    unittest.main()