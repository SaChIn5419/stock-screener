# Quant Screener Pro 🚀

An institutional-grade automated stock screener and quant analysis tool for the Indian Market (NSE). This tool combines advanced quantitative scoring, AI-powered sentiment analysis (NLP), and interactive visualizations to identify high-quality investment opportunities.

## Key Features

### 1. Professional Quant Model 🧠
We moved beyond basic screening to relative valuation and quality metrics:
-   **Z-Score Valuation**: Ranks stocks based on how cheap they are *relative to their Industry* (using **EV/EBITDA** or P/E).
-   **Quality Trifecta**: A composite score of **ROIC** (Efficiency), **Cash Conversion** (Real Profits), and **Interest Coverage** (Safety).
-   **Value Trap Filter**: Penalizes "cheap" stocks (Low P/E) that have shrinking earnings.
-   **Risk-Adjusted Momentum**: Calculates momentum using a **12M - 1M** "Brake" to avoid FOMO, adjusted for annual volatility.

### 2. AI Market Sentiment 📰
-   Uses **Google News RSS** to fetch real-time headlines.
-   Analyzes sentiment using **VADER** (Valence Aware Dictionary and sEntiment Reasoner), specifically tuned for financial text.
-   Provides a "Market Mood" (Bullish/Bearish/Neutral) score.

### 3. Institutional Data Validator 🛡️
-   **Penny Stock Filter**: Ignores stocks < ₹5.
-   **Liquidity Check**: Rejects stocks with zero volume for 3+ consecutive days.
-   **Fat Finger Detection**: Filters out unrealistic price spikes (>50%).
-   **Zombie Stock Filter**: Identifies stocks with zero volatility (flatlined) for 10+ days.

### 4. Interactive Dashboard 📊
-   Generates HTML reports using **Plotly**.
-   **Efficient Frontier**: Risk vs Return Scatter plot.
-   **Market Map**: Treemap weighted by Market Cap and colored by Score.
-   **Screener Diagnostic**: Parallel coordinates plot to trace stock characteristics.

### 5. Auto-Portfolio Builder 💰
-   Automatically allocates a hypothetical budget (e.g., ₹100,000).
-   Uses a **Score-Weighted** allocation strategy (Better stocks get more capital).

---

## Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/SaChIn5419/stock-screener.git
    cd stock-screener
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Run Nifty 50 Analysis (Fast)
```bash
python main.py --mode nifty50
```

### Run Full Market Analysis
```bash
python main.py --mode all --workers 20
```

### Output
-   **Console**: Real-time progress, Top 5 Picks, Sentiment Score, and Portfolio Allocation.
-   **Reports (`result/`)**:
    -   `stock_analysis_*.csv`: Full detailed dataset.
    -   `interactive_risk_return_*.html`: Interactive Scatter Plot.
    -   `sector_treemap_*.html`: Sector Visualization.

---

## Logic & Scoring

The **Final Score (0-100)** is a weighted composite of:
1.  **Quality (40%)**: ROIC + Cash Conversion + Interest Coverage.
2.  **Valuation (30%)**: Industry-Relative Z-Score (EV/EBITDA priority).
3.  **Momentum (30%)**: Risk-Adjusted 11-Month Return.

*Penalties are applied for Value Traps.*

---

## License
MIT License. Free for educational and personal use.
