import unittest

from crawl import normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html, get_images_from_html, extract_page_data


class TestCrawl(unittest.TestCase):
    # check https no slash
    def test_normalize_url_https(self):
        input_url = "https://www.boot.dev/blog/path"
        normalized_url = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(normalized_url, expected)

    # check https with slash
    def test_normalize_url_https_s(self):
        input_url = "https://www.boot.dev/blog/path/"
        normalized_url = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(normalized_url, expected)

    # check http no slash
    def test_normalize_url_http(self):
        input_url = "http://www.boot.dev/blog/path"
        normalized_url = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(normalized_url, expected)

    # check http with slash
    def test_normalize_url_http_s(self):
        input_url = "http://www.boot.dev/blog/path/"
        normalized_url = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(normalized_url, expected)

    # check return of <h1>
    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    # check return priority of <h1> over <h2>
    def test_get_heading_priority(self):
        input_body = "<html><body><h2>Subtitle</h2><h1>Main Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Main Title"
        self.assertEqual(actual, expected)

    # check return of <h2> when no <h1>
    def test_get_heading_from_html_h2(self):
        input_body = "<html><body><h2>Fallback Title</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Fallback Title"
        self.assertEqual(actual, expected)

    # check return of no <h1> or <h2>
    def test_get_heading_from_html_none(self):
            input_body = """<html lang="en">
            <head>
              <meta charset="UTF-8">
              <title>Sample</title>
            </head>
            <body>
              <main>
                <section class="card">
                  <strong>Name:</strong> <span>Jane Doe</span>
                </section>
                <table>
                  <tr><th>ID</th><th>Status</th></tr>
                  <tr><td>1</td><td>Active</td></tr>
                </table>
                <button type="button">Submit</button>
              </main>
            </body>
            </html>"""
            actual = get_heading_from_html(input_body)
            expected = ""
            self.assertEqual(actual, expected)

    # check <main> paragraph takes priority
    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
        <p>Outside paragraph.</p>
        <main>
            <p>Main paragraph.</p>
        </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    # check first paragraph with no <main>
    def test_get_first_paragraph_from_html_no_main(self):
        input_body = """<html><body>
        <p>First paragraph.</p>
        <p>Second paragraph.</p>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph."
        self.assertEqual(actual, expected)

    # check no <p> returns empty string
    def test_get_first_paragraph_from_html_none(self):
        input_body = """<html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>Sample</title>
        </head>
        <body>
          <main>
            <section class="card">
              <strong>Name:</strong> <span>Jane Doe</span>
            </section>
            <table>
              <tr><th>ID</th><th>Status</th></tr>
              <tr><td>1</td><td>Active</td></tr>
            </table>
            <button type="button">Submit</button>
          </main>
        </body>
        </html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    # check relative urls are converted to absolute
    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/about">About</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/about"]
        self.assertEqual(actual, expected)

    # check url extraction 1 url
    def test_get_urls_from_html(self):
        input_url = "https://crawler-test.com"
        input_body = """<html>
          <body>
            <a href="https://crawler-test.com">Go to Boot.dev</a>
            <img src="/logo.png" alt="Boot.dev Logo" />
          </body>
        </html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    # check multiple urls are extracted in order
    def test_get_urls_from_html_multiple(self):
        input_url = "https://crawler-test.com"
        input_body = """<html>
          <body>
            <nav>
              <a href="/">Home</a>
              <a href="/about">About</a>
              <a href="https://example.com/external">External</a>
            </nav>
            <main>
              <a href="/blog/post-1">Post 1</a>
              <a>No href here</a>
              <a href="contact">Contact</a>
            </main>
          </body>
        </html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/",
            "https://crawler-test.com/about",
            "https://example.com/external",
            "https://crawler-test.com/blog/post-1",
            "https://crawler-test.com/contact",
        ]
        self.assertEqual(actual, expected)

    # check relative image src is converted to absolute
    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    # check multiple images, skipping any without src
    def test_get_images_from_html_multiple(self):
        input_url = "https://crawler-test.com"
        input_body = """<html>
          <body>
            <img src="/logo.png" alt="Logo">
            <img src="https://cdn.example.com/banner.jpg" alt="Banner">
            <img alt="No src here">
            <img src="images/photo.webp" alt="Photo">
          </body>
        </html>"""
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/logo.png",
            "https://cdn.example.com/banner.jpg",
            "https://crawler-test.com/images/photo.webp",
        ]
        self.assertEqual(actual, expected)

    # check no images returns empty list
    def test_get_images_from_html_none(self):
        input_url = "https://crawler-test.com"
        input_body = """<html>
          <body>
            <h1>No Images</h1>
            <p>Just text and a <a href="/link">link</a>.</p>
          </body>
        </html>"""
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    #
    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)


if __name__=="__main__":
    unittest.main()