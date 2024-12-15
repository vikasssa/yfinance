from fastapi import FastAPI, HTTPException
import mysql.connector
import os
from pymongo import MongoClient
import pandas as pd
import google.generativeai as genai
from db_connector import get_connection_from_pool  # Import the DB connection from db_connector.py

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.get_database()
news_collection = db["news"]

app = FastAPI()

#GEmini key
APIKey = os.getenv('GEMINI_KEY')
genai.configure(api_key=APIKey)
model = genai.GenerativeModel("gemini-1.5-flash")

# Helper function to query stock data from MySQL
def query_stock_data(ticker: str):
    """
    Query stock data for a specific ticker symbol from the MySQL database.

    Parameters:
    - ticker (str): Stock ticker symbol.

    Returns:
    - pd.DataFrame: The queried stock data.
    """
    try:
        # Get a connection from the pool
        db_connection = get_connection_from_pool()
        cursor = db_connection.cursor(dictionary=True)

        # Prepare SQL query to fetch stock data for the ticker
        query = """
        SELECT * FROM stock_prices WHERE ticker = %s
        """

        # Execute the query
        cursor.execute(query, (ticker,))
        result = cursor.fetchall()

        # Convert result to DataFrame for easy manipulation
        df = pd.DataFrame(result)

        # Close the connection
        cursor.close()
        db_connection.close()

        return df

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error querying the database: {e}")


# Route to get the highest price for a specific stock ticker
@app.get("/stock/{ticker}/highest-price")
def get_highest_price(ticker: str):
    """
    Get the highest price for the stock ticker.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
    - dict: Highest stock price with timestamp.
    """
    try:
        df = query_stock_data(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail="Stock data not found for this ticker.")

        highest_row = df.loc[df['high_price'].idxmax()]
        highest_price = {
            "ticker": ticker,
            "timestamp": highest_row["timestamp"],
            "high_price": highest_row["high_price"]
        }
        return highest_price

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to get the lowest price for a specific stock ticker
@app.get("/stock/{ticker}/lowest-price")
def get_lowest_price(ticker: str):
    """
    Get the lowest price for the stock ticker.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
    - dict: Lowest stock price with timestamp.
    """
    try:
        df = query_stock_data(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail="Stock data not found for this ticker.")

        lowest_row = df.loc[df['low_price'].idxmin()]
        lowest_price = {
            "ticker": ticker,
            "timestamp": lowest_row["timestamp"],
            "low_price": lowest_row["low_price"]
        }
        return lowest_price

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to get the closing price for a specific stock ticker
@app.get("/stock/{ticker}/closing-price")
def get_closing_price(ticker: str):
    """
    Get the closing price for the stock ticker.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
    - dict: Closing stock price with timestamp.
    """
    try:
        df = query_stock_data(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail="Stock data not found for this ticker.")

        last_row = df.iloc[-1]
        closing_price = {
            "ticker": ticker,
            "timestamp": last_row["timestamp"],
            "close_price": last_row["close_price"]
        }
        return closing_price

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to get the closing price for a specific stock ticker
@app.get("/stock/{ticker}/all-rows")
def get_closing_price(ticker: str):
    """
    Get the closing price for the stock ticker.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g., 'AAPL').

    Returns:
    - dict: Closing stock price with timestamp.
    """
    try:
        df = query_stock_data(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail="Stock data not found for this ticker.")
        # Convert DataFrame to a list of dictionaries
        all_rows = df.to_dict(orient="records")
        return all_rows

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to get the summary for a specific stock ticker
@app.get("/stock/{ticker}/all-rows/{query}")
def get_stock_summary(ticker: str, query: str):
    """
    Get the summary for the stock ticker.

    Parameters:
    - ticker (str): Stock ticker symbol (e.g., 'AAPL').
    - query (str): user query

    Returns:
    - dict: response.
    """
    try:
        df = query_stock_data(ticker)
        if df.empty:
            raise HTTPException(status_code=404, detail="Stock data not found for this ticker.")
        # Convert DataFrame to a list of dictionaries
        all_rows = df.to_dict(orient="records")

        prompt = f"""
        Generate insightful answer for the query from  given context as below:
        If there is no context provided then say 'no relevant information is available in given context'.
        Do not make up answer on your own.
        Answer must be grounded from context.
        query : {query}
        context: {all_rows}
        """
        response = model.generate_content(prompt)
        return {"response":response.text}


    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/{ticker}/ai-news")
def get_ai_news(ticker: str):
    try:
        news = list(news_collection.find(
            {"ticker": ticker},
            {"_id": 0, "ticker": 1, "content": 1}
        ))
        return news
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/{ticker}/ai-news/{query}")
def get_ai_news_summary(ticker: str, query: str):
    try:
        news = list(news_collection.find(
            {"ticker": ticker},
            {"_id": 0, "ticker": 1, "content": 1}
        ))

        prompt = f"""
        Generate insightful answer for the query from  given context as below:
        If there is no context provided then say 'no relevant information is available in given context'.
        Do not make up answer on your own.
        Answer must be grounded from context.
        query : {query}
        context: {news}
        """
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))