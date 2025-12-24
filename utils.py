import pandas as pd
import requests
import io

def get_nifty50_tickers():
    """Returns a hardcoded list of major Nifty 50 tickers."""
    return [
        "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "ITC",
        "SBIN", "LICI", "KOTAKBANK", "HINDUNILVR", "LT", "AXISBANK", "BAJFINANCE",
        "HCLTECH", "ADANIENT", "ASIANPAINT", "TITAN", "MARUTI", "SUNPHARMA",
        "ULTRACEMCO", "TATASTEEL", "NTPC", "POWERGRID", "M&M", "JSWSTEEL",
        "LTIM", "ADANIPORTS", "TATASTAMPS", "COALINDIA", "SIEMENS", "SBILIFE",
        "BAJAJFINSV", "PIDILITIND", "TECHM", "NESTLEIND", "ONGC", "GRASIM",
        "HDFCLIFE", "GOACARBON" # Added a few more for good measure/demo
    ]

def get_all_nse_tickers(url="https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"):
    """
    Fetches all active NSE equity tickers from the official NSE CSV.
    Note: NSE website can be flaky with automated requests (anti-scraping).
    If it fails, it returns a fallback list.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        csv_content = response.content.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_content))
        return df['SYMBOL'].tolist()
    except Exception as e:
        print(f"Warning: Could not fetch live NSE list details: {e}")
        print("Returning Nifty 50 list as fallback.")
        return get_nifty50_tickers()
