import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

def generate_interactive_dashboard(df, report_dir="reports", timestamp=""):
    """
    Generates interactive HTML visualizations for deeper screener analysis.
    """
    if df.empty:
        print("Data insufficient for plotting.")
        return

    # Ensure report directory exists
    os.makedirs(report_dir, exist_ok=True)
    
    # --- PRE-PROCESSING ---
    # 1. Filter out extreme outliers for better zooming
    plot_df = df.copy()
    
    required_cols = ['Annual Volatility (%)', 'Annual Return (%)', 'Sector', 'Market Cap']
    missing = [c for c in required_cols if c not in plot_df.columns]
    if missing:
        print(f"Visualizer Warning: Missing columns for plotting: {missing}")
        return

    # Robust integer conversion for safety
    plot_df['Annual Volatility (%)'] = pd.to_numeric(plot_df['Annual Volatility (%)'], errors='coerce')
    plot_df['Annual Return (%)'] = pd.to_numeric(plot_df['Annual Return (%)'], errors='coerce')

    plot_df = plot_df[
        (plot_df['Annual Volatility (%)'] < 100) & 
        (plot_df['Annual Return (%)'] < 200) &
        (plot_df['Annual Return (%)'] > -50)
    ]
    
    # 2. Fill NaNs for display purposes
    plot_df['Sector'] = plot_df['Sector'].fillna('Unknown')
    plot_df['Market Cap'] = plot_df['Market Cap'].fillna(0)
    
    # Ensure Final_Score exists, else default to 0
    if 'Final_Score' not in plot_df.columns:
        plot_df['Final_Score'] = 0

    # =========================================================================
    # VISUAL 1: The "Efficient Frontier" (Risk vs Return) - Interactive
    # =========================================================================
    
    hover_cols = ['Current Price', 'P/E Ratio', 'Final_Score']
    hover_data = [c for c in hover_cols if c in plot_df.columns]

    fig_scatter = px.scatter(
        plot_df, 
        x='Annual Volatility (%)', 
        y='Annual Return (%)',
        color='Sector',                 # Color by Sector
        size='Market Cap',              # Size by Market Cap
        hover_name='Symbol',            
        hover_data=hover_data,
        title=f'Risk vs. Return: The Efficient Frontier ({timestamp})',
        template='plotly_dark',
        height=700
    )
    
    # Add average lines
    if not plot_df.empty:
        avg_x = plot_df['Annual Volatility (%)'].mean()
        avg_y = plot_df['Annual Return (%)'].mean()
        fig_scatter.add_vline(x=avg_x, line_width=1, line_dash="dash", line_color="white", annotation_text="Avg Risk")
        fig_scatter.add_hline(y=avg_y, line_width=1, line_dash="dash", line_color="white", annotation_text="Avg Return")

    scatter_path = os.path.join(report_dir, f"interactive_risk_return_{timestamp}.html")
    fig_scatter.write_html(scatter_path)
    print(f"Saved: {scatter_path}")

    # =========================================================================
    # VISUAL 2: The "Sector Map" (Treemap)
    # =========================================================================
    
    # We only take positive Market Caps
    tree_df = plot_df[plot_df['Market Cap'] > 0]
    
    if not tree_df.empty:
        fig_tree = px.treemap(
            tree_df, 
            path=[px.Constant("All Sectors"), 'Sector', 'Symbol'], 
            values='Market Cap',
            color='Final_Score',            
            color_continuous_scale='RdYlGn',
            title='Market Map: Size by Cap, Color by Screener Score',
            template='plotly_dark'
        )
        
        tree_path = os.path.join(report_dir, f"sector_treemap_{timestamp}.html")
        fig_tree.write_html(tree_path)
        print(f"Saved: {tree_path}")

    # =========================================================================
    # VISUAL 3: The "Screener Diagnostic" (Parallel Coordinates)
    # =========================================================================
    
    # We select top 50 stocks by Score to keep it readable
    top_50 = plot_df.sort_values('Final_Score', ascending=False).head(50)
    
    dims = ['Final_Score', 'P/E Ratio', 'ROE', 'Debt to Equity', 'Annual Volatility (%)']
    # Filter dims to only existing numeric columns
    dims = [d for d in dims if d in top_50.columns]
    
    # Needs to be numeric for Parallel Coords
    for d in dims:
         top_50[d] = pd.to_numeric(top_50[d], errors='coerce').fillna(0)

    if len(dims) > 1:
        fig_par = px.parallel_coordinates(
            top_50,
            dimensions=dims,
            color='Final_Score',
            color_continuous_scale=px.colors.diverging.Tealrose,
            title='Screener Logic Check: Characteristics of Top 50 Stocks',
            template='plotly_dark'
        )
        
        par_path = os.path.join(report_dir, f"screener_diagnostic_{timestamp}.html")
        fig_par.write_html(par_path)
        print(f"Saved: {par_path}")
