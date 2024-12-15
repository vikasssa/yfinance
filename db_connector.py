import mysql.connector
from mysql.connector import pooling
import os
import pandas as pd
import time

# Get MySQL connection info from environment variables
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root_password')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'stock_data')


# MySQL Connection Pool Configuration
def create_connection_pool():
    """
    Create and return a MySQL connection pool.
    """
    dbconfig = {
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "host": MYSQL_HOST,
        "database": MYSQL_DATABASE,
        "pool_name": "stock_pool",
        "pool_size": 5
    }

    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            pool = mysql.connector.pooling.MySQLConnectionPool(**dbconfig)
            return pool
        except mysql.connector.errors.DatabaseError as e:
            print(f"Error connecting to MySQL (Attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception("Failed to connect to MySQL after several attempts")


# Global connection pool
db_pool = create_connection_pool()


def get_connection_from_pool():
    """Get a connection from the pool."""
    return db_pool.get_connection()


def save_to_mysql(data, ticker_symbol):
    """
    Save the stock data to the MySQL database using a pooled connection.

    Parameters:
    - data (DataFrame): The stock data to save.
    - ticker_symbol (str): The stock ticker symbol.
    """
    try:
        # Get a connection from the pool
        db_connection = get_connection_from_pool()
        cursor = db_connection.cursor()

        # Prepare SQL query
        query = """
        INSERT INTO stock_prices (ticker, timestamp, open_price, high_price, low_price, close_price)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        # Iterate over the DataFrame and insert each row
        for index, row in data.iterrows():
            cursor.execute(query, (
                ticker_symbol,
                index,
                row['Open'],
                row['High'],
                row['Low'],
                row['Close']
            ))

        # Commit changes
        db_connection.commit()
        print(f"Saved {len(data)} records to the database for ticker: {ticker_symbol}")

    except mysql.connector.Error as e:
        print(f"Error saving to database: {e}")
    finally:
        if db_connection.is_connected():
            cursor.close()
            db_connection.close()


def save_to_csv(data, ticker_symbol):
    """Save stock data to a CSV file."""
    filename = f"stock_data_{ticker_symbol}.csv"
    data.to_csv(filename)
    print(f"Saved data to {filename}")
