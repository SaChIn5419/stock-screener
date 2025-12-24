# Automated Fundamental Analyzer

This project automates the fundamental analysis of NSE stocks using Python and `yfinance`. It fetches key metrics, calculates price returns, and computes a simple "Fundamental Score" to help identify potential investment opportunities.

## Features
- **Concurrent Data Fetching**: Uses multi-threading to speed up data retrieval.
- **Fundamental Scoring**: Rates stocks based on PE, ROE, Profit Margin, and Debt-to-Equity.
- **Nifty 50 or Full NSE Support**: Choose between a quick analysis of top stocks or a full market scan.
- **CSV Reporting**: Saves detailed results to the `reports/` directory.

## Prerequisite
Ensure you have Python installed. If using Anaconda, you are good to go.
Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Analyze Nifty 50 (Fast)
```bash
python main.py --mode nifty50
```

### 2. Analyze All NSE Stocks (Slower)
```bash
python main.py --mode all
```

### 3. Adjust Threading
To fetch faster (or slower to avoid rate limits), use `--workers`:
```bash
python main.py --mode nifty50 --workers 20
```

## Output
Results are saved in `reports/stock_analysis_[mode]_[timestamp].csv`.
The CSV includes:
- Price Returns (Daily, Weekly, Monthly)
- Valuation Metrics (PE, PEG, Price to Book)
- Financials (Revenue, Margins, EBITDA)
- **Fundamental Score**: A simple aggregated score (0-10) to highlight strong companies.
