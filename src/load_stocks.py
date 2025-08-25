import yfinance as yf
import pandas as pd
import numpy as np

# STEP 1: Choose your stock tickers (you can change/add more)
tickers = ["NDAQ", "CME", "ICE", "SPGI", "MCO", "MSCI"]

# STEP 2: Download last 6 months of daily data with all price types
print("🔄 Downloading stock data...")
raw_data = yf.download(tickers, period="6mo", interval="1d", auto_adjust=False)

# STEP 3: Extract only 'Adj Close' prices
data = raw_data["Adj Close"]

# STEP 4: Drop rows with missing data
data.dropna(inplace=True)

# STEP 5: Calculate daily returns (percentage change)
returns = data.pct_change().dropna()

# STEP 6: Compute mean returns and covariance matrix (risk)
mean_returns = returns.mean()
cov_matrix = returns.cov()

# STEP 7: Print summaries
print("\n✅ Stock Prices (last 5 days):")
print(data.tail())

print("\n📊 Daily Returns (last 5 days):")
print(returns.tail())

print("\n📈 Mean Returns (per stock):")
print(mean_returns)

print("\n⚠️ Covariance Matrix (Risk):")
print(cov_matrix)

# STEP 8: Save for later use in QAOA
data.to_csv("data/stock_prices.csv")
returns.to_csv("data/stock_returns.csv")
mean_returns.to_csv("data/mean_returns.csv")
cov_matrix.to_csv("data/cov_matrix.csv")

print("\n💾 All files saved in 'data/' folder!")