# Search Engine Tool — COMP3011 Coursework 2
Author: **Jia Xin Low**

This project implements a full search engine pipeline as required in the COMP3011 Web Services & Web Data coursework.  
The tool **crawls**, **indexes**, **stores**, and **searches** a target website: https://quotes.toscrape.com

The system includes:  
- A **polite web crawler** (6‑second delay)  
- An **inverted index** storing frequency + positions  
- A **command‑line interface** with `build`, `load`, `print`, `find` commands  
- A **search engine** supporting AND‑queries with **TF‑IDF relevance ranking**
- A **complete automated test suite** (crawler, indexer, search)  

---

# ⭐ 1. Overview

This tool performs the following tasks:

### ✔ Crawl  
Fetches all pages from the website following pagination (`Next` button), respecting a **6‑second politeness window**.

### ✔ Index  
Builds an inverted index of **every word**:  
- normalised (case-insensitive)  
- tracked by **frequency**  
- tracked by **positions**  

### ✔ Store & Load  
Index is saved to and loaded from a **single file** (`data/index.json`).

### ✔ Search  
Two types of search are supported:

| Command | Description |
|---------|-------------|
| `print <word>` | Shows every page containing the word + frequency + positions |
| `find <w1 w2 ...>` | AND‑search returning pages that contain **all** query words, ranked by **TF‑IDF relevance** |

This satisfies the functional requirements of the brief.

---

# ⭐ 2. Project Structure
```bash
SearchEngineCW2/
│
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   └── main.py
│
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   ├── test_search.py
│   └── test_cli_integration.py
│
├── data/
│   └── index.json (generated after build)
│   └── test_index.json (generated after tests)
│
├── requirements.txt
└── README.md
```

---

# ⭐ 3. Architecture and Design Rationale
The system is intentionally structured as a **modular, command‑driven pipeline**:

Crawler → Indexer → SearchEngine → CLI

- **Crawler:** Responsible solely for polite HTTP retrieval and HTML parsing. It follows pagination, enforces a 6‑second politeness window, and converts raw HTML into structured PageData objects.
- **Indexer:** Converts structured page content into an inverted index, tracking word frequency and positional information per page. Index construction and persistence are handled independently of querying.
- **SearchEngine:** Performs query processing and ranking on top of the in‑memory inverted index, supporting single‑word lookup, multi‑word AND‑search, and TF‑IDF relevance ranking. It operates independently of crawling and storage.
- **CLI (main.py):** Acts as the orchestration layer, coordinating user input and command execution without embedding core application logic.

This separation of concerns improves testability, maintainability, and clarity. Each component can be tested in isolation (e.g. crawler with mocked HTTP requests, search with synthetic indices) while also supporting integration-style testing of the full pipeline.

## Command-to-Component Workflow
Each CLI command activates a specific subset of the system:
- **build** → Crawler → Indexer → save index to disk
- **load** → load index file into memory via the Indexer
- **print <word>** → SearchEngine → single‑word index lookup
- **find <words>** → SearchEngine → AND‑search with TF‑IDF ranking
This design avoids unnecessary computation (e.g. re‑crawling during search), ensures predictable command behaviour, and keeps interactive usage responsive.

---

# ⭐ 4. Installation Instructions

### 1. Clone the repository
```bash
git clone <your repo URL>
cd SearchEngineCW2
```
### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate    # Windows
# OR
source venv/bin/activate # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

# ⭐ 5. Running the CLI Tool
Run:
```bash
python src/main.py
```

When the CLI starts, type commands such as:

## ✔ Help command
The CLI includes a built‑in help menu to guide usage:
```bash
> help
```

Example output:
```bash
Available Commands:
  build                Crawl website, build index, save to file
  load                 Load index from data/index.json
  print <word>         Show index entry for a word
  find <w1 w2 ...>     AND-search, ranked using TF-IDF
  help                 Show this help menu
  exit                 Quit the application

Examples:
  print life
  find good friends
```
This command improves usability and discoverability of features.

## ✔ Build index (crawl → index → save)
```bash
> build
```
This will:
- crawl all pages
- build the inverted index
- save it into data/index.json

## ✔ Load index
```bash
> load
```

## ✔ Print word index entry
```bash
> print wisdom
```

Example output:
```bash
Word: wisdom
 - Page: https://quotes.toscrape.com/page/3/
   Frequency: 1
   Positions: [14]
```

## ✔ AND‑search with TF‑IDF ranking
Only pages containing all query terms are returned. Search operates at the page level using AND-intersection over indexed pages, not at the individual quote level.

This page-level search simplifies the indexing and retrieval logic while remaining consistent with the coursework requirements, which do not mandate quote-level or positional phrase matching.
```bash
> find life
```

Example output:
```bash
Pages ranked by TF-IDF relevance:
1. https://quotes.toscrape.com/page/2/ (score = 1.7851)
2. https://quotes.toscrape.com/page/6/ (score = 0.8926)
3. https://quotes.toscrape.com/ (score = 0.6694)
```

## ✔ Multi‑word queries use the same AND‑search logic
```bash
> find truth lies
```

## ✔ Exit CLI
```bash
> exit
```

---

# ⭐ 6. Advanced Feature: TF‑IDF Relevance Ranking
To improve search quality, the search engine implements **TF‑IDF (Term Frequency–Inverse Document Frequency) ranking**, an information‑retrieval technique that balances:

- **Term Frequency (TF)**: how often a word appears on a page
- **Inverse Document Frequency (IDF)**: how rare the word is across all pages

For multi‑word queries, TF‑IDF scores are **summed across all query terms**, and pages are returned in descending order of relevance.
This ensures that pages where query terms are more prominent appear first.

---

# ⭐ 7. Algorithmic Complexity Considerations 
Let:
- N = total number of indexed word occurrences across all pages
- D = total number of pages
- Q = number of query terms

**Index construction**
- Time complexity: Indexing runs in O(N) time, as each word occurrence is processed exactly once during indexing.
- Space complexity: O(N), storing frequency and positional information for each indexed word occurrence.

**Search Operations**
- AND‑search (find): Page intersection runs in O(Q · D) in the worst case, followed by scoring only on the intersected result set.
- TF‑IDF scoring: Runs in O(Q · R), where R is the number of result pages after intersection.

To support IDF computation, the total document count is **precomputed once during SearchEngine initialisation**, avoiding repeated scanning of the index during queries.

**Command-Level Perspective**

From a user’s perspective:
- **build** is the most expensive operation, dominated by crawling latency and index construction.
- **load** runs in linear time relative to index size and avoids recomputation.
- **print** is near O(1) average‑case due to dictionary lookup.
- **find** scales with query size and result set, enabling efficient interactive querying.

These trade‑offs are appropriate for the target dataset size and prioritise correctness, clarity, and maintainability over premature optimisation.

---

# ⭐ 8. Testing Instructions
The project includes a full test suite with **21 tests**, covering:
- crawler logic (with mocked HTTP requests)
- inverted index construction (frequency, positions, multi-page behaviour)
- search functionality (print, AND-search, case-insensitivity)
- TF-IDF ranking behaviour
- save/load persistence
- integration between indexing and search components

To run all tests:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

You should see:
```bash
Ran 21 tests
OK
```
The majority of core logic is exercised by automated tests, including edge cases such as empty queries and missing terms. Overall test coverage is high across functional components, and the CLI workflow is validated through integration-style tests without requiring network access.

---

# ⭐ 9. Dependencies
Installed via requirements.txt:
```bash
requests
beautifulsoup4
```
Both libraries are recommended in the coursework brief.

# ⭐ 10. GenAI Usage Declaration
This project used GenAI (Microsoft Copilot) for:
- helping structure modules (crawler.py, indexer.py, search.py)
- debugging and refining logic
- generating initial test scaffolding
- writing documentation (README.md)
- resolving certain HTML parsing issues
- learning alternative approaches and validating code correctness

## My Independent Work
- I implemented, modified, validated, and debugged all code myself.
- I fully understand all parts of the codebase and can explain them during the demonstration.
- All AI-generated suggestions were reviewed, rewritten, and corrected for accuracy.

# ⭐ 11. Notes for Assessors
The project:
- Works on Windows, macOS, and Linux
- Does not require network access during testing (crawler tests are fully mocked)
- Matches the required folder structure
- Includes complete test coverage
- Provides all four required CLI commands
- Demo-ready for recording
Please run:
```bash
python src/main.py
```
to start the CLI.