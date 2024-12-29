Description:

This POC implements a stock data analysis system that integrates multiple services. The mysql service stores stock data, while the stock-fetcher periodically fetches stock data based on user-defined tickers. The stock-news-fetcher scrapes relevant news articles using the splash service, storing them in MongoDB (mongodb). The FastAPI service (fastapi) serves as the central component, querying both the MySQL database for stock data and MongoDB for news, while also interacting with the Gemini language model to generate insights. A Streamlit front-end (streamlit) visualizes the stock data and insights, providing an interactive user experience





cd yfinance/

vi docker-compose.yml file
  Add your gemini key in docker compose file under fastapi service

  
docker-compose up --build

wait for sometime untill all services are up and running

open http://localhost:8501/ in your local browser


screenshots:

![image](https://github.com/user-attachments/assets/03c5a08f-36be-4eb9-92d1-f228a454ae2d)





<img width="1288" alt="Screenshot 2024-12-15 at 5 55 46 PM" src="https://github.com/user-attachments/assets/b8e632c6-f57b-4a6b-870f-68c7f5571a94" />




<img width="1288" alt="Screenshot 2024-12-15 at 5 56 15 PM" src="https://github.com/user-attachments/assets/c378686d-e84d-46bd-bc41-c4ee947ec391" />





<img width="1461" alt="Screenshot 2024-12-15 at 6 31 31 PM" src="https://github.com/user-attachments/assets/453dc05c-6032-4a49-abcc-4537a7595720" />

