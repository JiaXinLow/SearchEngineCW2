import time
import logging
from dataclasses import dataclass
from typing import Callable, Optional, List
import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------
# Logging Configuration
# ----------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(console_handler)

# ----------------------------------------------------------
# Data Models
# ----------------------------------------------------------

@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]

@dataclass
class PageData:
    url: str
    quotes: List[Quote]

# ----------------------------------------------------------
# Crawler Class (OOP)
# ----------------------------------------------------------

class Crawler:
    """
    High-quality, production-style web crawler for https://quotes.toscrape.com.

    Features:
    - 6 second politeness window (per assignment spec)
    - Clean OOP design
    - Error handling & retry logic
    - BeautifulSoup parsing
    - Pagination handling
    - Dependency injection for testability
    """

    def __init__(
        self,
        base_url: str = "https://quotes.toscrape.com",
        request_func: Callable = requests.get,
        politeness_delay: int = 6,
        timeout: int = 10
    ):
        self.base_url = base_url.rstrip("/")
        self.request_func = request_func
        self.politeness_delay = politeness_delay
        self.timeout = timeout

    # ----------------------------------------------------------
    # Fetch Page
    # ----------------------------------------------------------
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetches a single page with retry logic and politeness delay.
        Returns the HTML string or None if failed.
        """
        logger.info(f"Fetching: {url}")

        for attempt in range(2):   # try twice
            try:
                response = self.request_func(url, timeout=self.timeout)
                response.raise_for_status()

                logger.debug("Fetch successful.")
                time.sleep(self.politeness_delay)  # 6 seconds required
                return response.text

            except requests.exceptions.RequestException as e:
                logger.warning(f"Error fetching {url}: {e}")
                logger.info(f"Retrying ({attempt+1}/2)...")
                time.sleep(2)

        logger.error(f"Failed to fetch {url} after retries.")
        return None

    # ----------------------------------------------------------
    # Parse Page
    # ----------------------------------------------------------
    def parse_page(self, html: str, url: str) -> PageData:
        """
        Extracts clean structured data from HTML using BeautifulSoup.
        Returns PageData with Quote objects.
        """
        soup = BeautifulSoup(html, "html.parser")

        quote_blocks = soup.find_all("div", class_="quote")
        quotes: List[Quote] = []

        for block in quote_blocks:
            try:
                text = block.find("span", class_="text").get_text(strip=True)
                author = block.find("small", class_="author").get_text(strip=True)
                tags = [tag.get_text(strip=True)
                        for tag in block.find_all("a", class_="tag")]

                quotes.append(Quote(text=text, author=author, tags=tags))

            except AttributeError:
                logger.error("Malformed quote block — skipping.")
                continue

        return PageData(url=url, quotes=quotes)

    # ----------------------------------------------------------
    # Pagination
    # ----------------------------------------------------------
    def get_next_page(self, html: str) -> Optional[str]:
        """
        Detects the 'Next' pagination button and returns the absolute URL.
        """
        soup = BeautifulSoup(html, "html.parser")
        next_link = soup.find("li", class_="next")

        if not next_link:
            return None

        relative = next_link.a["href"]  # e.g. "/page/2/"
        next_url = f"{self.base_url}{relative}"
        return next_url

    # ----------------------------------------------------------
    # Main Crawler Run
    # ----------------------------------------------------------
    def run(self) -> List[PageData]:
        """
        Crawls all pages starting from base_url.
        Returns a list of PageData objects.
        """
        logger.info("Starting crawl...")

        all_pages: List[PageData] = []
        current_url = f"{self.base_url}/"

        while True:
            html = self.fetch_page(current_url)
            if html is None:
                logger.error(f"Skipping page due to repeated fetch failure: {current_url}")
                break

            page_data = self.parse_page(html, current_url)
            all_pages.append(page_data)

            next_url = self.get_next_page(html)
            if not next_url:
                logger.info("No more pages. Crawl complete.")
                break

            logger.info(f"Next page → {next_url}")
            current_url = next_url

        logger.info(f"Total pages crawled: {len(all_pages)}")
        return all_pages


# ----------------------------------------------------------
# Debug / Manual Execution
# ----------------------------------------------------------
if __name__ == "__main__":
    crawler = Crawler()
    data = crawler.run()
    print(f"Crawled {len(data)} pages.")