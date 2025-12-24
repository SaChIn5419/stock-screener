import feedparser
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import urllib.parse

class MarketSentiment:
    """
    Analyzes market sentiment using Google Finance News RSS and NLP (VADER).
    """
    
    @staticmethod
    def fetch_news(query="Nifty 50", days=1):
        """
        Fetches top news headlines from Google News RSS.
        """
        # ceid=IN:en ensures Indian news context
        base_url = "https://news.google.com/rss/search"
        search_query = f"{query} when:{days}d"
        # URL Encode the query to handle spaces and special chars
        encoded_query = urllib.parse.quote(search_query)
        
        url = f"{base_url}?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        try:
            feed = feedparser.parse(url)
            news_list = []
            
            # Limit to top 15 to get a good sample without too much noise
            for entry in feed.entries[:15]:
                news_list.append({
                    'Title': entry.title,
                    'Link': entry.link,
                    'Published': entry.published
                })
            
            return pd.DataFrame(news_list)
        except Exception as e:
            print(f"Error fetching news: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_market_mood(queries=["Nifty 50", "Indian Economy", "Sensex"]):
        """
        Fetches news for multiple key terms and calculates an aggregate sentiment score.
        Returns: (Score, Mood, DataFrame of Headlines)
        """
        all_news = []
        
        print("Fetching market news...")
        for q in queries:
            df = MarketSentiment.fetch_news(q)
            if not df.empty:
                all_news.append(df)
        
        if not all_news:
            return 0, "Neutral (No Data)", pd.DataFrame()
            
        final_df = pd.concat(all_news).drop_duplicates(subset=['Title'])
        
        # Calculate Sentiment using VADER (Better for finance/short text)
        # Polarity: -1 (Negative) to +1 (Positive)
        analyzer = SentimentIntensityAnalyzer()
        final_df['Polarity'] = final_df['Title'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
        
        avg_polarity = final_df['Polarity'].mean()
        
        # Scale to 0-100 for easier reading (0=Bearish, 50=Neutral, 100=Bullish)
        # Map [-0.5, 0.5] range to [0, 100] approximately
        # Polarity rarely hits perfect -1 or 1 in news titles, usually within -0.3 to 0.3
        score = 50 + (avg_polarity * 100) 
        score = max(0, min(100, score)) # Clamp
        
        # Determine Mood Label
        if score >= 60:
            mood = "Bullish 🟢"
        elif score <= 40:
            mood = "Bearish 🔴"
        else:
            mood = "Neutral 🟡"
            
        return round(score, 1), mood, final_df
