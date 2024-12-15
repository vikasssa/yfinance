import yfinance as yf
from pymongo import MongoClient
import json
import os
import time
from datetime import datetime
import schedule
from scrapy_news_spider import fetch_text_using_scrapy
import multiprocessing


# Get MongoDB URI from environment variable
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/stock_news_db")
client = MongoClient(mongo_uri)
db = client["stock_news_db"]
collection = db["news"]

# List of AI-related keywords to filter news
AI_KEYWORDS = ["artificial intelligence", "machine learning", "deep learning", "neural network",
               "ai technology","generative ai","llm","large language model"]

# Read tickers and mode from environment variables
tickers = os.getenv("TICKERS", "AAPL, MSFT").split(",")  # Default tickers if not set in env
mode = os.getenv("MODE", "once").lower()  # Default mode is "once" if not set in env


# Function to fetch stock news metadata from Yahoo Finance
def fetch_stock_news(ticker):
    stock = yf.Ticker(ticker)
    news_data = stock.news
    return news_data


# Function to check if the article is related to AI
def is_ai_related(content):
    content = content.lower()  # Convert to lowercase for case-insensitive comparison
    for keyword in AI_KEYWORDS:
        if keyword in content:
            return True
    return False


# Function to scrape the full content (text only) of the news article
def scrape_article_content(url):
    try:
        content = fetch_text_using_scrapy([url])
        # print(f"content-fetched: {content}")
        if content:
            article_content = ""
            for article  in content:
                article_content += article['text']

            return article_content
        else:
            return None
    except Exception as e:
        print(f"Error scraping article {url}: {e}")
        return None


# Function to save news metadata and content to MongoDB
def save_news_to_mongo(news_data, ticker):
    urls = []
    try:
        for news in news_data:
            urls.append(news['link'])
        p = multiprocessing.Process(target=fetch_text_using_scrapy, args=(urls,))
        p.start()
        p.join()
        # Read the scraped data from the output.json file
        if os.path.exists('output.json'):
            with open('output.json', 'r') as f:
                content = json.load(f)
                # After reading the content, delete the output file
                os.remove('output.json')
                for article in content:
                    article_url = article['url']
                    #print(f"url: {article_url}")
                    content = article['text']
                    a = 'Bid Wealth Invest ETF Report Streaming'
                    b = 'View comments'
                    cc = content.split(a)[-1]
                    article_content = cc.split(b)[0]
                    #print(f"content {article_content}")

                    if article_content:
                        # Check if the content is AI-related
                        if is_ai_related(article_content):

                            # Create a document with title, content, date, and ticker
                            article = {
                                "ticker": ticker,
                                "url": article_url,
                                "content": article_content,  # Store the content of the article
                            }

                            # Insert the article into MongoDB collection
                            collection.insert_one(article)
                            print(f"Saved AI-related article for: {article_url}")
                        else:
                            print(f"Article is not AI-related: {article_url}")
                    else:
                        print(f"Failed to fetch content for article: {article_url}")
    except Exception as e:
        print(f"exception {str(e)}")



# Function to run the script in "once" mode or "schedule" mode
def run():
    try:
        for ticker in tickers:
            print(f"Fetching news for {ticker}")
            news_data = fetch_stock_news(ticker)

            if news_data:
                save_news_to_mongo(news_data, ticker)
            else:
                print(f"No news data found for {ticker}")

            # Wait before fetching news for the next ticker
            time.sleep(5)
    except Exception as e:
        print(f"Exception as {str(e)}")


# Main function
def main():
    try:
        run()
        if mode == "schedule":
            print(f"Scheduling stock news fetch for tickers: {tickers}")
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            # Schedule the task every day at the same time (e.g., at 10:00)
            schedule.every().day.at(current_time).do(run)  # Adjust the time as per your preference
            while True:
                schedule.run_pending()
                time.sleep(1)
    except Exception as e:
        print(f"Exception as {str(e)}")


if __name__ == "__main__":
    main()
