# Web Scraper: A Command-Line Site Crawler in Python

## Project Status
**Complete (v1)** — the core crawler works: given a starting URL, it visits pages on the same site, extracts key data from each one, and writes a report. Possible extensions are listed in the roadmap below.

## Overview
A command-line web scraper built with Python. Starting from a single URL, it crawls the pages of that website concurrently by following internal links, collects structured data from each page, and exports the results to a JSON report. It avoids revisiting pages by normalizing URLs, so `example.com/page` and `example.com/page/` are treated as the same page.

> Built as part of the [Boot.dev](https://www.boot.dev) backend development curriculum. This is a guided learning project, not an original design. Its purpose was to practice HTTP requests, HTML parsing, recursion, and testing.

## What it does
- Takes a starting URL, a concurrency limit, and a maximum page count as command-line arguments
- Fetches multiple pages at the same time using `asyncio`
- Parses the HTML of each page
- Extracts data from each page: the main heading (`<h1>`, falling back to `<h2>`), the first paragraph (preferring one inside `<main>`), outgoing links, and image URLs
- Converts relative links and image paths into absolute URLs
- Follows internal links only, staying within the starting site
- Normalizes URLs (ignoring trailing slashes and the URL scheme) to avoid duplicate visits
- Skips pages that return an error status or aren't HTML, and keeps crawling
- Stops after the maximum number of pages is reached
- Writes the collected data to a JSON report

## Data Collected Per Page
| Field | Description |
|---|---|
| `url` | The page's URL |
| `heading` | Text of the first `<h1>` (or `<h2>` if there is no `<h1>`) |
| `first_paragraph` | Text of the first paragraph, preferring one inside `<main>` |
| `outgoing_links` | Absolute URLs of every link found on the page |
| `image_urls` | Absolute URLs of every image found on the page |

## Tools & Methods
- **Python** — core language
- **asyncio** and **aiohttp** — asynchronous, concurrent page fetching
- **requests** — fetching pages in the original synchronous version of the crawler
- **BeautifulSoup** — parsing HTML and extracting elements
- **unittest** (Python standard library) — 18 unit tests covering URL normalization and the HTML parsing functions
- **uv** — dependency and environment management
- Concurrent crawling with a configurable limit, URL normalization, and defensive handling of failed requests

## What I Practiced
- Writing asynchronous code with `async`/`await`
- Limiting how many requests run at once (with an `asyncio.Semaphore`) so a crawl doesn't overwhelm a server
- Protecting shared state across concurrent tasks with an `asyncio.Lock`
- Managing an HTTP session cleanly with an async context manager
- Using type hints and `TypedDict` to describe the structure of page data
- Making HTTP requests and handling errors and non-HTML responses
- Parsing HTML to extract text, links, and images
- Resolving relative URLs into absolute ones
- Writing unit tests for small, single-purpose functions, including edge cases like missing tags, links without an `href`, and images without a `src`
- Tracking state across a crawl to avoid loops and duplicate work
- Structuring crawl results into a JSON report

## Responsible Use
Only run this against sites you own or have permission to crawl, and keep the crawl small by using a low concurrency limit and page cap. The crawler identifies itself with a custom `User-Agent` header. Aggressive crawling can overload a server and may violate a site's terms of service. This is a learning project and does not implement `robots.txt` handling or advanced rate limiting.

## How to Run
**Requirements:** Python 3 and [uv](https://docs.astral.sh/uv/)

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/webscraper.git
   cd webscraper
   ```
2. Run the crawler, passing a starting URL, the maximum number of concurrent requests, and the maximum number of pages to crawl:
   ```bash
   uv run main.py https://example.com 3 25
   ```
   This crawls up to 25 pages of `example.com`, with at most 3 requests in flight at a time, then writes a JSON report.
3. Run the tests:
   ```bash
   uv run python -m unittest
   ```

## Next Steps / Roadmap
- Add `robots.txt` support
- Add rate limiting between requests
- Add tests for the async crawler and the HTTP error handling
- Add a crawl depth limit
- Export results in additional formats (e.g., CSV)

## Repo Structure
```
├── main.py              # entry point: reads arguments and starts the crawl
├── crawl.py             # HTML parsing, URL handling, and sync + async crawlers
├── json_report.py       # writes crawl results to a JSON report
├── tests/               # unit tests
├── pyproject.toml       # project metadata and dependencies
├── .gitignore
└── README.md
```
