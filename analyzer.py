import yfinance as yf
import pandas as pd
import numpy as np
import concurrent.futures
import time
from validator import DataValidator

class StockAnalyzer:
    def __init__(self):
        pass

    def get_stock_fundamentals(self, symbol):
        """
        Fetches fundamental data and calculates price returns for a given stock symbol.
        """
        try:
            # Append .NS for NSE stocks if not present
            ticker_symbol = f"{symbol}.NS" if not symbol.endswith('.NS') else symbol
            
            stock = yf.Ticker(ticker_symbol)
            
            # --- 1. Get Historical Data for Returns Calculation ---
            # Fetch 1 year of data for Risk/Return analysis
            hist = stock.history(period="1y")
            
            # --- Data Validation (Institutional Check) ---
            is_valid, reason = DataValidator.check_data_quality(hist)
            if not is_valid:
                print(f"Skipping {symbol}: {reason}")
                return None

            current_price = hist['Close'].iloc[-1]
            
            # --- RISK / RETURN METRICS ---
            annual_return = 0
            annual_volatility = 0
            sharpe_ratio = 0
            max_drawdown = 0
            
            if len(hist) > 1:
                # Calculate Daily Returns
                hist['Daily_Return'] = hist['Close'].pct_change()
                
                # 1. Annualized Return (Mean daily return * 252 trading days)
                avg_daily_return = hist['Daily_Return'].mean()
                annual_return = ((1 + avg_daily_return) ** 252) - 1
                
                # 2. Annualized Volatility (Standard Deviation * sqrt(252))
                daily_volatility = hist['Daily_Return'].std()
                annual_volatility = daily_volatility * np.sqrt(252)
                
                # 3. Sharpe Ratio (Risk Free Rate approx 7%)
                risk_free_rate = 0.07
                if annual_volatility > 0:
                    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
                    
                # 4. Max Drawdown
                cum_returns = (1 + hist['Daily_Return']).cumprod()
                running_max = cum_returns.cummax()
                drawdown = (cum_returns - running_max) / running_max
                max_drawdown = drawdown.min()
            
            # Calculate Standard Returns
            daily_change = 0
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                daily_change = ((current_price - prev_close) / prev_close) * 100
                
            six_month_change = 0
            if len(hist) >= 126:
                six_month_price = hist['Close'].iloc[-126]
                six_month_change = ((current_price - six_month_price) / six_month_price) * 100
            elif len(hist) > 0:
                start_price = hist['Close'].iloc[0]
                six_month_change = ((current_price - start_price) / start_price) * 100

            # --- PRO FEATURE: Momentum with a Brake (12M - 1M) ---
            momentum_12m_1m = 0
            risk_adjusted_momentum = 0
            
            if len(hist) >= 252:
                price_12m_ago = hist['Close'].iloc[-252] 
                price_1m_ago = hist['Close'].iloc[-21] if len(hist) >= 21 else current_price
                
                momentum_12m_1m = ((price_1m_ago - price_12m_ago) / price_12m_ago)
                
                if annual_volatility > 0:
                    risk_adjusted_momentum = momentum_12m_1m / annual_volatility
            else:
                 # Fallback
                if len(hist) > 21:
                    price_start = hist['Close'].iloc[0]
                    price_1m_ago = hist['Close'].iloc[-21]
                    momentum_12m_1m = ((price_1m_ago - price_start) / price_start)
                    if annual_volatility > 0:
                        risk_adjusted_momentum = momentum_12m_1m / annual_volatility

            # --- 2. Get Fundamental Data from .info ---
            info = stock.info
            
            pe = info.get('trailingPE')
            forward_pe = info.get('forwardPE')
            ev_ebitda = info.get('enterpriseToEbitda')
            roe = info.get('returnOnEquity')
            roic = info.get('returnOnCapital') # often missing
            
            fcf = info.get('freeCashflow')
            
            # ... (rest of the fetching logic is fine)
            net_income = info.get('netIncomeToCommon')
            
            interest_coverage = info.get('interestCoverage')
            if interest_coverage is None:
                try:
                    financials = stock.financials
                    if not financials.empty and 'Ebit' in financials.index and 'Interest Expense' in financials.index:
                        ebit = financials.loc['Ebit'].iloc[0]
                        interest = financials.loc['Interest Expense'].iloc[0]
                        if interest != 0:
                            interest_coverage = abs(ebit / interest)
                except:
                    pass
            
            profit_margin = info.get('profitMargins')
            debt_to_equity = info.get('debtToEquity')
            
            data = {
                'Symbol': symbol,
                'Company Name': info.get('longName'),
                'Sector': info.get('sector'),
                'Industry': info.get('industry'),
                'Current Price': round(current_price, 2),
                'Daily Change (%)': round(daily_change, 2),
                '6M Return (%)': round(six_month_change, 2),
                'Momentum_12M_1M': momentum_12m_1m,
                'Risk_Adjusted_Momentum': risk_adjusted_momentum,
                'Annual Return (%)': round(annual_return * 100, 2),
                'Annual Volatility (%)': round(annual_volatility * 100, 2),
                'Sharpe Ratio': round(sharpe_ratio, 2),
                'Max Drawdown (%)': round(max_drawdown * 100, 2),
                'Market Cap': info.get('marketCap'),
                'P/E Ratio': pe,
                'Forward PE': info.get('forwardPE'),
                'EV/EBITDA': ev_ebitda,
                'PEG Ratio': info.get('pegRatio'),
                'Price to Book': info.get('priceToBook'),
                'Dividend Yield': info.get('dividendYield'),
                'ROE': roe,
                'ROIC': roic,
                'Free Cash Flow': fcf,
                'Net Income': net_income,
                'Interest Coverage': interest_coverage,
                'Debt to Equity': debt_to_equity,
                'Profit Margin': profit_margin,
                'Earnings Growth': info.get('earningsGrowth'),
                'Revenue Growth': info.get('revenueGrowth'),
            }
            return data

        except Exception as e:
            return None

    def filter_universe(self, df, min_market_cap=50000000000, min_price=10):
        if df.empty: return df
        initial_count = len(df)
        df['Market Cap'] = pd.to_numeric(df['Market Cap'], errors='coerce')
        df['Current Price'] = pd.to_numeric(df['Current Price'], errors='coerce')
        df_filtered = df[(df['Market Cap'] >= min_market_cap) & (df['Current Price'] >= min_price)]
        filtered_count = len(df_filtered)
        print(f"Universe Filter: Retained {filtered_count}/{initial_count} stocks (Removed {initial_count - filtered_count} penny/smallcap stocks).")
        return df_filtered.copy()

    def calculate_quant_score(self, df):
        if df.empty: return df
        df = df.copy()

        numeric_cols = ['P/E Ratio', 'Earnings Growth', 'ROE', 'ROIC', 'Free Cash Flow', 'Net Income', 'Interest Coverage', 'Risk_Adjusted_Momentum']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 1. VALUE TRAP
        pe_clean = df['P/E Ratio'].fillna(999)
        growth_clean = df['Earnings Growth'].fillna(0)
        df['Is_Value_Trap'] = (pe_clean < 10) & (growth_clean < 0)
        
        trap_count = df['Is_Value_Trap'].sum()
        if trap_count > 0:
            print(f"Warning: Detected {trap_count} potential Value Traps (Low P/E + Neg Growth). These will be penalized.")

        # 2. Z-SCORE NORMALIZATION (Relative Valuation)
        # Upgrade: Prioritize EV/EBITDA > P/E Ratio
        
        # Create a composite 'Valuation_Metric' column
        # If EV/EBITDA is present and positive, use it. Else use P/E.
        # We fill NaNs with a high value (expensive) to avoid errors
        
        df['EV/EBITDA'] = pd.to_numeric(df['EV/EBITDA'], errors='coerce')
        
        # Strategy: Create a new column 'Valuation_Metric' for the Z-Score
        df['Valuation_Metric'] = df['EV/EBITDA'].fillna(df['P/E Ratio'])
        
        # Cleaning: If even P/E is missing, fill with high number
        df['Valuation_Metric'] = df['Valuation_Metric'].fillna(100)

        df['Industry'] = df['Industry'].fillna('Unknown')
        
        # Calculate stats per industry based on this new metric
        industry_stats = df.groupby('Industry')['Valuation_Metric'].agg(['mean', 'std', 'count'])
        
        def calculate_z(row):
            ind = row['Industry']
            val = row['Valuation_Metric']
            
            if pd.isna(val): return 10
            if ind not in industry_stats.index: return 0
            
            stats = industry_stats.loc[ind]
            if stats['count'] < 3 or pd.isna(stats['std']) or stats['std'] == 0:
                univ_mean = df['Valuation_Metric'].mean()
                univ_std = df['Valuation_Metric'].std()
                if univ_std == 0: return 0
                return (val - univ_mean) / univ_std
            
            return (val - stats['mean']) / stats['std']

        df['Valuation_Z_Score'] = df.apply(calculate_z, axis=1)
        df['Value_Rank'] = df['Valuation_Z_Score'].rank(ascending=True)
        df['Value_Score'] = 100 - (df['Value_Rank'] / len(df) * 100)

        # 3. QUALITY TRIFECTA
        df['Metric_Efficiency'] = df['ROIC'].fillna(df['ROE']).fillna(0)
        
        def calc_cash_conv(row):
            fcf = row['Free Cash Flow']
            ni = row['Net Income']
            if pd.isna(fcf) or pd.isna(ni) or ni <= 0: return 0
            return fcf / ni
            
        df['Metric_Cash_Conv'] = df.apply(calc_cash_conv, axis=1)
        df['Metric_Safety'] = df['Interest Coverage'].fillna(0)
        
        df['Rank_Efficiency'] = df['Metric_Efficiency'].rank(ascending=True)
        df['Rank_Cash_Conv'] = df['Metric_Cash_Conv'].rank(ascending=True)
        df['Rank_Safety'] = df['Metric_Safety'].rank(ascending=True)
        
        df['Avg_Quality_Rank'] = (df['Rank_Efficiency'] + df['Rank_Cash_Conv'] + df['Rank_Safety']) / 3
        df['Quality_Score'] = df['Avg_Quality_Rank'] / len(df) * 100

        # 4. MOMENTUM
        df['Mom_Metric'] = df['Risk_Adjusted_Momentum'].fillna(-100)
        df['Momentum_Rank'] = df['Mom_Metric'].rank(ascending=True)
        df['Momentum_Score'] = df['Momentum_Rank'] / len(df) * 100

        # FINAL SCORE
        df['Final_Score'] = (
            (0.40 * df['Quality_Score']) + 
            (0.30 * df['Value_Score']) + 
            (0.30 * df['Momentum_Score'])
        ).round(1)
        
        df.loc[df['Is_Value_Trap'], 'Final_Score'] = df.loc[df['Is_Value_Trap'], 'Final_Score'] * 0.5
        
        return df

    def analyze_stocks(self, ticker_list, max_workers=10):
        results = []
        total = len(ticker_list)
        print(f"Starting analysis for {total} stocks with {max_workers} threads...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {executor.submit(self.get_stock_fundamentals, ticker): ticker for ticker in ticker_list}
            completed = 0
            for future in concurrent.futures.as_completed(future_to_ticker):
                data = future.result()
                if data:
                    results.append(data)
                completed += 1
                if completed % 10 == 0:
                    print(f"Processed {completed}/{total} stocks...")

        end_time = time.time()
        print(f"Fetch complete. Processed {total} stocks in {end_time - start_time:.2f} seconds.")
        return pd.DataFrame(results)
