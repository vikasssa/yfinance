import os

import streamlit as st
import requests

# Define the FastAPI base URL (update with your container's URL or service name)
FASTAPI_BASE_URL = os.getenv("FASTAPI_URL","http://localhost:8000")  # Replace with the actual URL of your FastAPI container


# Define Streamlit UI
def main():
    st.title("Stock Query and News Viewer")

    # Sidebar for functionality selection
    option = st.sidebar.selectbox(
        "Choose Functionality",
        ["Query Stock Data", "Query AI News Articles"]
    )

    # Query stock data functionality
    if option == "Query Stock Data":
        st.subheader("Query All Stock Rows")

        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL):", "")
        query = st.text_input("Enter Query for Filtering Rows (optional):", "")

        if st.button("Fetch Stock Data"):
            if ticker:
                try:
                    response = requests.get(f"{FASTAPI_BASE_URL}/stock/{ticker}/all-rows/{query}")
                    if response.status_code == 200:
                        data = response.json()
                        st.write(f"Results for ticker: {ticker}")
                        st.dataframe(data)
                    else:
                        st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to FastAPI service: {e}")
            else:
                st.warning("Please enter a valid stock ticker.")

    # Query AI news articles functionality
    elif option == "Query AI News Articles":
        st.subheader("Query AI News Articles for Stock")

        ticker = st.text_input("Enter Stock Ticker (e.g., MSFT):", "")
        query = st.text_input("Enter Query to Filter AI News (optional):", "")

        if st.button("Fetch AI News"):
            if ticker:
                try:
                    response = requests.get(f"{FASTAPI_BASE_URL}/stock/{ticker}/ai-news/{query}")
                    if response.status_code == 200:
                        data = response.json()
                        st.write(f"Results for ticker: {ticker}")
                        st.dataframe(data)
                    else:
                        st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to FastAPI service: {e}")
            else:
                st.warning("Please enter a valid stock ticker.")


# Run the app
if __name__ == "__main__":
    main()
