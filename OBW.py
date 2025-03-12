import requests
import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import time

# Initialize exchange
exchange = ccxt.coinbase()

# Fetch historical data from CoinGecko
def fetch_data(symbol='ethereum', currency='usd', days=18):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {'vs_currency': currency, 'days': days, 'interval': 'daily'}
    response = requests.get(url, params=params)
    data = response.json()
    prices = data['prices']
    volumes = data['total_volumes']

    df = pd.DataFrame(prices, columns=['timestamp', 'close'])
    df['volume'] = [v[1] for v in volumes]
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Detect accumulation phase
def detect_accumulation(df):
    support_level = df['close'].rolling(window=15).min()
    resistance_level = df['close'].rolling(window=15).max()

    sideways = (df['close'] > support_level) & (df['close'] < resistance_level)
    high_volume = df['volume'] > df['volume'].rolling(window=15).mean() * 1.5

    df['accumulation'] = sideways & high_volume
    return df, support_level, resistance_level

# Fetch the order book
def fetch_order_book(symbol: str):
    return exchange.fetch_order_book(symbol)

# Identify stop-loss liquidity clusters
def identify_stop_loss_clusters(order_book, num_bins=100):
    bids = np.array(order_book['bids'])
    asks = np.array(order_book['asks'])

    bid_prices, bid_volumes = bids[:, 0], bids[:, 1]
    ask_prices, ask_volumes = asks[:, 0], asks[:, 1]

    price_range = np.linspace(min(bid_prices.min(), ask_prices.min()), max(bid_prices.max(), ask_prices.max()), num_bins + 1)

    bid_clusters, _ = np.histogram(bid_prices, bins=price_range, weights=bid_volumes)
    ask_clusters, _ = np.histogram(ask_prices, bins=price_range, weights=ask_volumes)

    bid_clusters = gaussian_filter1d(bid_clusters, sigma=2)
    ask_clusters = gaussian_filter1d(ask_clusters, sigma=2)
    return bid_clusters, ask_clusters, price_range

# Calculate volume percentages
def calculate_volume_percentages(bid_clusters, ask_clusters):
    total_bid_volume = bid_clusters.sum()
    total_ask_volume = ask_clusters.sum()
    total_volume = total_bid_volume + total_ask_volume

    if total_volume == 0:
        return 0.0, 0.0

    bid_percentage = (total_bid_volume / total_volume) * 100
    ask_percentage = (total_ask_volume / total_volume) * 100
    return bid_percentage, ask_percentage

# Determine trade action
def determine_trade_action(accumulation, bid_percentage, ask_percentage, threshold=10.0):
    if accumulation and bid_percentage > ask_percentage + threshold:
        return "LONG"
    elif not accumulation and ask_percentage > bid_percentage + threshold:
        return "SHORT"
    else:
        return "NEUTRAL"

# Main function
if __name__ == '__main__':
    symbol = 'ETH/USD'
    historical_data = fetch_data('ethereum', days=18)
    processed_data, support, resistance = detect_accumulation(historical_data)

    plt.ion()
    plt.figure(figsize=(14, 7))

    while True:
        try:
            # Real-time order book analysis
            order_book = fetch_order_book(symbol)
            current_price = order_book['asks'][0][0]

            bid_clusters, ask_clusters, price_range = identify_stop_loss_clusters(order_book)
            bid_percentage, ask_percentage = calculate_volume_percentages(bid_clusters, ask_clusters)

            # Detect if in accumulation zone
            is_accumulation = processed_data['accumulation'].iloc[-1]

            # Determine trade action
            trade_action = determine_trade_action(is_accumulation, bid_percentage, ask_percentage)
            print(f"\nCurrent Price: {current_price:.2f}")
            print(f"Bid Volume %: {bid_percentage:.2f} | Ask Volume %: {ask_percentage:.2f}")
            print(f"Trade Action: {trade_action}")

            # Visualization
            plt.clf()
            plt.subplot(2, 1, 1)
            plt.plot(processed_data['timestamp'], processed_data['close'], label='Close Price', color='blue')
            plt.plot(processed_data['timestamp'], support, label='Support Level', color='green')
            plt.plot(processed_data['timestamp'], resistance, label='Resistance Level', color='red')
            plt.fill_between(processed_data['timestamp'], processed_data['close'], where=processed_data['accumulation'],
                             color='yellow', alpha=0.5, label='Accumulation Zone')
            plt.axhline(y=current_price, color='orange', linestyle='--', label='Current Price')
            plt.title("ETH Price & Accumulation Phase")
            plt.xlabel("Date")
            plt.ylabel("Price (USD)")
            plt.legend()

            # Plot liquidity clusters
            plt.subplot(2, 1, 2)
            plt.bar(price_range[:-1], bid_clusters, width=np.diff(price_range), color='green', alpha=0.6, label='Bids')
            plt.bar(price_range[:-1], ask_clusters, width=np.diff(price_range), color='red', alpha=0.6, label='Asks')
            plt.axvline(x=current_price, color='orange', linestyle='--', label='Current Price')
            plt.title("Liquidity Clusters")
            plt.xlabel("Price")
            plt.ylabel("Volume")
            plt.legend()

            plt.tight_layout()
            plt.pause(0.1)

            time.sleep(5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
