import unittest
from unittest.mock import Mock

from crawler import Crawler, PageData, Quote

# ------------------------------------------------------
# Helper HTML samples for mocking
# ------------------------------------------------------

PAGE_1_HTML = """
<html>
  <body>
    <div class="quote">
      <span class="text">"Quote A"</span>
      <span><small class="author">Author A</small></span>
      <div class="tags">
        <a class="tag">life</a>
        <a class="tag">wisdom</a>
      </div>
    </div>
    <li class="next">/page/2/Next</a></li>
  </body>
</html>
"""

PAGE_2_HTML = """
<html>
  <body>
    <div class="quote">
      <span class="text">"Quote B"</span>
      <span><small class="author">Author B</small></span>
      <div class="tags">
        <a class="tag">love</a>
      </div>
    </div>
  </body>
</html>
"""

ERROR_HTML = None  # to simulate failed fetch


class TestCrawler(unittest.TestCase):

    # --------------------------------------------------
    # Test: Single Page Crawl (no pagination)
    # --------------------------------------------------
    def test_single_page_crawl(self):
        mock_request = Mock()
        mock_request.return_value.text = PAGE_1_HTML
        mock_request.return_value.raise_for_status = lambda: None

        crawler = Crawler(request_func=mock_request)
        
        # override politeness delay to avoid sleep
        crawler.politeness_delay = 0

        html = crawler.fetch_page("http://dummy")
        self.assertIn("Quote A", html)

    # --------------------------------------------------
    # Test: Pagination (two pages)
    # --------------------------------------------------
    def test_pagination_two_pages(self):
        # Mock two responses in sequence
        mock_request = Mock(side_effect=[
            Mock(text=PAGE_1_HTML, raise_for_status=lambda: None),
            Mock(text=PAGE_2_HTML, raise_for_status=lambda: None),
        ])

        crawler = Crawler(request_func=mock_request)
        crawler.politeness_delay = 0

        pages = crawler.run()

        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[0].url, "https://quotes.toscrape.com/")
        self.assertEqual(pages[1].url, "https://quotes.toscrape.com/page/2/")

    # --------------------------------------------------
    # Test: Error Handling (failed fetch)
    # --------------------------------------------------
    def test_error_handling_failed_fetch(self):
        # simulate network failure
        mock_request = Mock(side_effect=Exception("Network error"))

        crawler = Crawler(request_func=mock_request)
        crawler.politeness_delay = 0

        html = crawler.fetch_page("http://dummy-url")
        self.assertIsNone(html)

    # --------------------------------------------------
    # Test: Parsed Data Format
    # --------------------------------------------------
    def test_parse_data_format(self):
        crawler = Crawler()
        page = crawler.parse_page(PAGE_1_HTML, "http://dummy")

        self.assertIsInstance(page, PageData)
        self.assertEqual(page.url, "http://dummy")
        self.assertEqual(len(page.quotes), 1)

        q = page.quotes[0]
        self.assertIsInstance(q, Quote)
        self.assertEqual(q.author, "Author A")
        self.assertIn("life", q.tags)


if __name__ == "__main__":
    unittest.main()