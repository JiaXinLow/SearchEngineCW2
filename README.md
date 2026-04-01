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
│   └── test_search.py
│
├── data/
│   └── index.json (generated after build)
│
├── requirements.txt
└── README.md
```

---

# ⭐ 3. Installation Instructions

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

# ⭐ 4. Running the CLI Tool
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
Only pages containing **all query terms in the same quote block** are returned. Results are ranked by TF‑IDF relevance, with higher‑scoring pages appearing first.
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

## ✔ ✔ Multi‑word queries use the same AND‑search logic
```bash
> find truth lies
```

## ✔ Exit CLI
```bash
> exit
```

---

# ⭐ 5. Advanced Feature: TF‑IDF Relevance Ranking
To improve search quality, the search engine implements **TF‑IDF (Term Frequency–Inverse Document Frequency) ranking**, an information‑retrieval technique that balances:

- **Term Frequency (TF)**: how often a word appears on a page
- **Inverse Document Frequency (IDF)**: how rare the word is across all pages

For multi‑word queries, TF‑IDF scores are **summed across all query terms**, and pages are returned in descending order of relevance.
This ensures that pages where query terms are more prominent appear first.

---

# ⭐ 6. Testing Instructions
The project includes a full test suite with **20 tests**, covering:
- crawler
- indexer
- search functionality and TF‑IDF ranking
To run all tests:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

You should see:
```bash
Ran 20 tests
OK
```
This test suite meets the coursework requirement for thorough automated testing.

---

# ⭐ 7. Dependencies
Installed via requirements.txt:
```bash
requests
beautifulsoup4
```
Both libraries are recommended in the coursework brief.

# ⭐ 8. GenAI Usage Declaration
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

# ⭐ 9. Notes for Assessors
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