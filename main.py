import os
import argparse
from datetime import datetime
from utils import get_nifty50_tickers, get_all_nse_tickers
from analyzer import StockAnalyzer
from visualizer import generate_interactive_dashboard
from sentiment import MarketSentiment

def main():
    parser = argparse.ArgumentParser(description="Automated Stock Fundamental Analyzer")
    parser.add_argument('--mode', type=str, choices=['nifty50', 'all'], default='nifty50',
                        help="Choose 'nifty50' for top 50 stocks or 'all' for all NSE stocks.")
    parser.add_argument('--workers', type=int, default=10,
                        help="Number of concurrent threads for data fetching.")
    
    args = parser.parse_args()

    # --- 0. Market Sentiment Check (New Feature) ---
    print("\n--- MARKET SENTIMENT (AI Powered) ---")
    score, mood, news_df = MarketSentiment.get_market_mood()
    print(f"Market Mood: {mood} (Score: {score}/100)")
    
    if not news_df.empty:
        print("\nTop Headlines driving the market:")
        # Show top 3 headlines
        for i, row in news_df.head(3).iterrows():
            print(f"- {row['Title']}")
    print("-" * 40 + "\n")

    # 1. Get Tickers
    if args.mode == 'all':
        print("Fetching full NSE stock list (this may take a moment)...")
        tickers = get_all_nse_tickers()
    else:
        print("Using Nifty 50 stock list.")
        tickers = get_nifty50_tickers()

    print(f"Total tickers to process: {len(tickers)}")

    # 2. Run Analysis
    analyzer = StockAnalyzer()
    df_results = analyzer.analyze_stocks(tickers, max_workers=args.workers)

    if df_results.empty:
        print("No data found or all requests failed.")
        return

    # 3. Filter Universe (Pro Standard)
    # Only keep stocks with > 5000 Cr Market Cap and > 10 INR Price
    # This removes "Noise" from the analysis
    print("Applying Universe Filter (Market Cap > 5000Cr)...")
    df_results = analyzer.filter_universe(df_results, min_market_cap=50000000000, min_price=10)
    
    if df_results.empty:
        print("No stocks passed the universe filter criteria.")
        return

    # 4. Calculate Quant Scores on Filtered Data
    # We do this AFTER filtering so ranks are relative to the "Investable Universe"
    print("Calculating Quant Models...")
    df_results = analyzer.calculate_quant_score(df_results)

    # 5. Granular Insights (Targeted News for Top Picks)
    # We sort by Score to find the 'Winners'
    if 'Final_Score' in df_results.columns:
        df_results = df_results.sort_values(by='Final_Score', ascending=False)
    
    top_picks = df_results.head(5)
    
    print("\n--- TOP 5 STOCKS (With News Context) ---")
    
    cols_to_show = ['Symbol', 'Current Price', 'Final_Score', 'PE_Z_Score', 'Quality_Score', 'Momentum_Score', 'Is_Value_Trap']
    cols_to_show = [c for c in cols_to_show if c in df_results.columns]
    print(top_picks[cols_to_show].to_string(index=False))
    
    print("\nFetching specific news for top picks...")
    for idx, row in top_picks.iterrows():
        symbol = row['Symbol']
        print(f"\n> News for {symbol}:")
        # Reuse existing fetch_news but specific to the company name
        # We strip .NS for better news search
        clean_name = row['Company Name'] if row.get('Company Name') else symbol
        company_news = MarketSentiment.fetch_news(clean_name, days=2)
        
        if not company_news.empty:
            for i, news_item in company_news.head(2).iterrows():
                print(f"  - {news_item['Title']}")
        else:
            print("  - No recent news found.")

    # 6. Interactive Save (User Control)
    print("\n" + "="*50)
    choice = input("Do you want to save the Detailed Report and Plots? (y/n): ").strip().lower()
    
    if choice == 'y':
        # Create reports directory if not exists
        report_dir = "reports"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_analysis_{args.mode}_{timestamp}.csv"
        filepath = os.path.join(report_dir, filename)
        
        df_results.to_csv(filepath, index=False)
        print(f"\n[Saved] CSV Report: {filepath}")
        
        # Generator Plot
        print("[Saved] Interactive Dashboard & Visuals...")
        generate_interactive_dashboard(df_results, report_dir, timestamp)
        
    else:
        print("\n[Discarded] Report was not saved.")

if __name__ == "__main__":
    main()
