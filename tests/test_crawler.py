import unittest
from unittest.mock import Mock
import requests
import sys, os

# ensure src/ is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from crawler import Crawler, PageData, Quote


# -----------------------------
# CORRECT, UNESCAPED HTML
# -----------------------------
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

    <li class="next"><a href="/page/2/">Next</a></li>
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


class TestCrawler(unittest.TestCase):

    def test_single_page_crawl(self):
        mock_request = Mock()
        mock_response = Mock()
        mock_response.text = PAGE_1_HTML
        mock_response.raise_for_status = lambda: None
        mock_request.return_value = mock_response

        crawler = Crawler(request_func=mock_request)
        crawler.politeness_delay = 0

        html = crawler.fetch_page("http://dummy")
        self.assertIn("Quote A", html)

    def test_pagination_two_pages(self):
        mock_request = Mock(side_effect=[
            Mock(text=PAGE_1_HTML, raise_for_status=lambda: None),
            Mock(text=PAGE_2_HTML, raise_for_status=lambda: None),
        ])

        crawler = Crawler(base_url="http://dummy", request_func=mock_request)
        crawler.politeness_delay = 0

        pages = crawler.run()

        self.assertEqual(len(pages), 2)
        self.assertEqual(pages[0].url, "http://dummy/")
        self.assertEqual(pages[1].url, "http://dummy/page/2/")

    def test_error_handling_failed_fetch(self):
        mock_request = Mock(side_effect=requests.exceptions.RequestException("Error"))

        crawler = Crawler(request_func=mock_request)
        crawler.politeness_delay = 0

        html = crawler.fetch_page("http://dummy")
        self.assertIsNone(html)

    def test_parse_data_format(self):
        crawler = Crawler()
        page = crawler.parse_page(PAGE_1_HTML, "http://dummy")

        self.assertIsInstance(page, PageData)
        self.assertEqual(page.url, "http://dummy")
        self.assertEqual(len(page.quotes), 1)

        q = page.quotes[0]
        self.assertEqual(q.author, "Author A")
        self.assertIn("life", q.tags)


if __name__ == "__main__":
    unittest.main()