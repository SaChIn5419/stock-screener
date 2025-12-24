import pandas as pd
import numpy as np

class DataValidator:
    """
    Institutional-grade data validation optimized for Small Caps & High Volatility.
    """
    
    @staticmethod
    def check_data_quality(hist_df, min_price=5.0):
        """
        Returns: (bool, reason)
        """
        # 0. Basic Integrity
        if hist_df is None or hist_df.empty:
            return False, "Empty DataFrame"
        
        # Sort index to ensure time-based logic works (Crucial fix)
        hist_df = hist_df.sort_index()

        # 1. Price Threshold (The "Penny Stock" Filter)
        # Institutions usually avoid stocks under Rs 5 or $1 because spreads are huge.
        last_price = hist_df['Close'].iloc[-1]
        if last_price < min_price:
            return False, f"Penny Stock Risk: Price {last_price} < {min_price}"

        # 2. Zeros/NaNs (The "Data Gap" Check)
        if hist_df['Close'].isnull().any() or (hist_df['Close'] == 0).any():
            return False, "Corrupt Data: Contains NaNs or Zeros"

        # 3. Liquidity Check (THE SWEET SPOT FIX)
        # Instead of checking if PRICE moves, check if VOLUME exists.
        # Small caps can have flat prices, but they must have volume.
        # Rule: Reject if Volume is 0 for > 3 consecutive days.
        if 'Volume' in hist_df.columns:
            zero_vol_streak = (hist_df['Volume'] == 0).rolling(window=3).sum()
            if (zero_vol_streak >= 3).any():
                return False, "Illiquidity Risk: No trading volume for 3+ consecutive days"
        
        # 4. The "Fat Finger" Spike Detector (Adaptive)
        # We separate "High Volatility" from "Bad Data".
        # Bad Data usually reverts instantly (Up 50%, Down 50%).
        pct_change = hist_df['Close'].pct_change()
        
        # Upper Limit: 20% is the standard Circuit Limit in India/many markets.
        # We allow up to 25% to account for slight data discrepancies.
        # Anything above 50% is almost certainly a Split/Bonus error.
        if (pct_change > 0.50).any():
            # Exception: Check if it's a Micro Cap (High Volatility is normal)
            # If price < 20, we allow more volatility.
            if last_price > 20: 
                return False, "Data Error: Unrealistic >50% single-day jump"

        # 5. Stale Price Check (Refined)
        # Only fail if price is flat AND Volume is low.
        # If Volume is high but price is flat, that's "Accumulation" (Good Signal).
        price_is_flat = (pct_change == 0)
        flat_streak = price_is_flat.rolling(window=10).sum() # Relaxed to 10 days
        
        # But we only care if it's flat for 10 days straight
        if (flat_streak >= 10).any():
            # Secondary check: Is this just a stable stock?
            # We look at the standard deviation of the last 30 days.
            recent_volatility = hist_df['Close'].tail(30).std()
            if recent_volatility < (last_price * 0.001): # Extremely low volatility
                 return False, "Zombie Stock: Price completely unchanged for 10+ days"

        return True, "Passed"
