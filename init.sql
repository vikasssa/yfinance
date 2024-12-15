-- init.sql: Initialize the stock_data database and create the stock_prices table
CREATE DATABASE IF NOT EXISTS stock_data;

USE stock_data;

CREATE TABLE IF NOT EXISTS stock_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    timestamp DATETIME NOT NULL,
    open_price DECIMAL(10, 2),
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2)
);
