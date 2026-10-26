import requests
import asyncio
import aiohttp
from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict


# expecting "www.boot.dev/blog/path"
def normalize_url(input_url: str) -> str:
    parsed_url = urlsplit(input_url)
    path = parsed_url.path.rstrip("/")
    fixed_url = f"{parsed_url.hostname}{path}"
    return fixed_url

# html header scraping
def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    header = soup.find("h1")
    if not header:
        header = soup.find("h2")
    return header.get_text(strip=True) if isinstance(header, Tag) else ""


# html paragraph scraping
def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find("main")
    scope = main if isinstance(main, Tag) else soup
    p_tag = scope.find("p")
    return p_tag.get_text(strip=True) if p_tag else ""

# extract url from html
def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    for anchor in soup.find_all("a"):
        if not isinstance(anchor, Tag):
            continue
        href = anchor.get("href")
        if href:
            urls.append(urljoin(base_url, str(href)))
    return urls

# get images from html
def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    for img in soup.find_all("img"):
        if not isinstance(img, Tag):
            continue
        src = img.get("src")
        if src:
            urls.append(urljoin(base_url, str(src)))
    return urls

# creating a class for the dictionary
class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

# extract page data to dictionary
def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }

# get exception responses
def get_html(url):
    response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    
    if response.status_code >= 400:
        raise Exception(f"Error: got status {response.status_code}")
    
    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise Exception(f"Error: expected text/html, got {content_type}")

    return response.text

# page crawl
def crawl_pages(
    base_url: str,
    current_url: str | None = None,
    page_data: dict[str, PageData] | None = None,
    ) -> dict[str, PageData]:
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}

    # check if still on same site
    if urlsplit(current_url).hostname != urlsplit(base_url).hostname:
        return page_data

    # check if already crawled
    normalized = normalize_url(current_url)
    if normalized in page_data:
        return page_data
    
    print(f"crawling: {current_url}")

    try:
        html = get_html(current_url)
    except Exception as e:
        print(f"skipping {current_url}: {e}")
        return page_data

    data = extract_page_data(html, current_url)
    page_data[normalized] = data

    for link in data["outgoing_links"]:
        crawl_pages(base_url, link, page_data)

    return page_data

# shared state management
class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency: int = 5, max_pages: int = 10):
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).hostname
        self.page_data: dict[str, PageData] = {}
        self.visited: set[str] = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks: set[asyncio.Task] = set()
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None

    # initialize session
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    # end session
    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    # adding page visits
    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.should_stop:
                return False
            
            if normalized_url in self.visited:
                return False
            
            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False
            
            self.visited.add(normalized_url)
            return True

    async def get_html(self, url: str):
        if self.session is None:
            raise Exception("session not started, use 'async with AsyncCrawler(...)'")
        async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as response:

            if response.status >= 400:
                raise Exception(f"Error: got status {response.status}")

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                raise Exception(f"Error: expected text/html, got {content_type}")

            return await response.text()

    # page crawl
    async def crawl_page(
        self,
        current_url: str | None = None,
        ):
        if self.should_stop:
            return
        
        if current_url is None:
            current_url = self.base_url

        # check if still on same site
        if urlsplit(current_url).hostname != self.base_domain:
            return 

        # check if already crawled
        normalized = normalize_url(current_url)
        if not await self.add_page_visit(normalized):
            return

        async with self.semaphore:
            print(f"crawling: {current_url}")

            try:
                html = await self.get_html(current_url)
            except Exception as e:
                print(f"skipping {current_url}: {e}")
                return

            data = extract_page_data(html, current_url)

        async with self.lock:
            self.page_data[normalized] = data

        tasks = []
        for link in data["outgoing_links"]:
            task = asyncio.create_task(self.crawl_page(link))
            tasks.append(task)
            self.all_tasks.add(task)
        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                self.all_tasks.discard(task)

    async def crawl(self) -> dict[str, PageData]:
        await self.crawl_page(self.base_url)
        return self.page_data

async def crawl_site_async(base_url: str, max_concurrency: int = 5, max_pages: int = 10) -> dict[str, PageData]:
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()