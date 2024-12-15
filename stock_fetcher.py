import os

import yfinance as yf
import schedule
import time
from db_connector import save_to_mysql, save_to_csv
from datetime import datetime

# Multithreading can be used to speed up
def fetch_stock_data(tickers, period, output):
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        data['timestamp'] = data.index
        if output == "db":
            save_to_mysql(data, ticker)
        elif output == "csv":
            save_to_csv(data, ticker)

def main():
    tickers = os.getenv("TICKERS", "AAPL,").split(",")
    mode = os.getenv("MODE",'once')
    output = os.getenv("OUTPUT","db")

    # Fetch stock data
    fetch_stock_data(tickers,'1mo', output)

    if mode == "schedule":
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        # Schedule the task every day if mode is "schedule"
        schedule.every().day.at(current_time).do(lambda: fetch_stock_data(tickers,'1d', output))
        while True:
            schedule.run_pending()
            time.sleep(1)



if __name__ == "__main__":
    main()
