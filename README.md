# Ethereum Trading Analysis Tool

This project is a Python-based tool designed to analyze Ethereum (ETH) market data and provide real-time trading insights. It integrates historical data from CoinGecko and real-time order book data from Coinbase to detect accumulation phases and liquidity clusters, ultimately suggesting trade actions (LONG, SHORT, or NEUTRAL).

## Features
- Fetches 18 days of historical ETH/USD data from CoinGecko.
- Detects accumulation phases based on price support/resistance and volume analysis.
- Analyzes Coinbase order book data to identify stop-loss liquidity clusters.
- Calculates bid/ask volume percentages to inform trade decisions.
- Visualizes price trends, accumulation zones, and liquidity clusters in real-time using Matplotlib.

## Requirements
- Python 3.x
- Libraries: `requests`, `ccxt`, `pandas`, `numpy`, `matplotlib`, `scipy`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
<img width="1126" alt="Screenshot 2025-03-11 at 9 14 19 PM" src="https://github.com/user-attachments/assets/5b482c9f-8965-4981-a403-eed2b27fa5a2" />
<img width="1126" alt="Screenshot 2025-03-11 at 9 14 19 PM" src="https://github.com/user-attachments/assets/dfd44976-82f7-452f-bd1e-1497023288ae" />

