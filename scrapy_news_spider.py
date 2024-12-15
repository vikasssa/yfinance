from xml.sax import parse

import scrapy
from scrapy_splash import SplashRequest
from scrapy.crawler import CrawlerProcess
import os
import re

SPLASH_URL = os.getenv('SPLASH_URL','http://localhost:8050')


class TextScraper(scrapy.Spider):
    name = 'text_scraper'

    # Define custom settings (including the User-Agent and Splash settings)
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Mediapartners-Google',
        'SPLASH_URL': SPLASH_URL,  # Splash service URL
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        'SPIDER_MIDDLEWARES': {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    }

    def start_requests(self):
        """
        Use SplashRequest to send requests through Splash for rendering JavaScript-heavy pages.
        """
        try:
            for url in self.start_urls:
                yield SplashRequest(
                    url,
                    self.parse,
                    endpoint='render.html',
                    args={'wait': 2},  # Adjust wait time for rendering
                )
        except:
            pass

    def parse(self, response):
        try:
            # Extract the main body of text
            body_text = self.extract_text(response)

            # Clean the text (strip out extra spaces and newlines)
            cleaned_text = " ".join([text.strip() for text in body_text if text.strip()])

            # Output the cleaned text
            yield {'url': response.url, 'text': cleaned_text}
        except Exception as e:
            print(f"exception: { str(e)}")
            return  None

    def extract_text(self, response):
        try:
            """
            Extract all text content from a webpage and filter out unwanted elements
            """
            # Extract raw text from the <body> tag while ignoring <script>, <style>, etc.
            body_text = response.xpath('//body//*[not(self::script or self::style)]//text()').getall()

            # Clean the text by removing unwanted content
            body_text = self.clean_text(body_text)

            return body_text
        except Exception as e:
            print(f"Exception as {str(e)}")
            return ""

    def clean_text(self, body_text):
        try:
            """
            Clean the raw extracted text by removing unwanted characters or elements
            """
            cleaned_text = []
            for text in body_text:
                text = text.strip()

                # Skip empty strings or unwanted data
                if not text or self.is_unwanted(text):
                    continue

                cleaned_text.append(text)

            return cleaned_text
        except Exception as e:
            print(f"Exception as {str(e)}")
            return ""


def is_unwanted(self, text):
        """
        Check if the text is unwanted (e.g., JavaScript code or inline scripts)
        """
        try:
            # Define unwanted patterns or keywords
            unwanted_patterns = [
                r"(?i)(window\.|document\.|function\(|var\s|let\s|const\s)",  # JS code
                r"\{.*?\}",  # Inline JSON or JS objects
                r"\(.*?\)",  # Inline JS function calls
                r";",  # Semicolon-heavy text (likely JS)
                r"[=:]{2,}",  # JS-like assignment operators
            ]

            # Remove text matching any unwanted patterns
            for pattern in unwanted_patterns:
                if re.search(pattern, text):
                    return True

            # Optional: Remove short texts or texts with excessive symbols
            if len(text) < 5 or sum(1 for char in text if char.isalnum()) / len(text) < 0.5:
                return True

            return False
        except Exception as e:
            print(f"Exception as {str(e)}")
            return False


def fetch_text_using_scrapy(urls):
    """
    Function to run the Scrapy process and return extracted content.
    """
    # Set up the Scrapy crawler process
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json',  # Save output to a JSON file
        'ROBOTSTXT_OBEY': True  # Make sure you respect robots.txt rules
    })

    try:
        # Start the crawl process
        process.crawl(TextScraper, start_urls=urls)
        process.start()  # Start the scraping process
    except Exception as e:
        print(f"exception {str(e)}")

