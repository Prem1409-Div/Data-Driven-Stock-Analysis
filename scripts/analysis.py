import os
import pandas as pd

# Define updated input and output directories
base_dir = r"C:\Users\Premkumar.Nagendran\OneDrive - Agilisium Consulting India Private Limited\Mini Projects\Data-Driven Stock Analysis"
input_dir = os.path.join(base_dir, "processed_data", "individual_stocks")
output_dir = os.path.join(base_dir, "processed_data", "visualization_data")
sector_file = os.path.join(base_dir, "processed_data", "Sector_data - Sheet1.csv")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

def load_stock_data(input_dir, only_close_prices=False):
    """Load stock data from CSV files into a dictionary."""
    stock_data = {}
    for file in os.listdir(input_dir):
        if file.endswith(".csv"):
            ticker = file.replace(".csv", "")
            df = pd.read_csv(os.path.join(input_dir, file))
            df["date"] = pd.to_datetime(df["date"])
            df.sort_values(by="date", inplace=True)
            if only_close_prices:
                df.set_index("date", inplace=True)
                stock_data[ticker] = df["close"]  # Store only closing prices
            else:
                stock_data[ticker] = df
    return stock_data

def calculate_volatility(stock_data):
    """Calculate yearly volatility for each stock."""
    volatility_data = []
    
    for ticker, df in stock_data.items():
        df["daily_return"] = df["close"].pct_change()
        yearly_volatility = df["daily_return"].std()
        volatility_data.append({"Ticker": ticker, "Yearly Volatility": yearly_volatility})
    
    volatility_df = pd.DataFrame(volatility_data)
    output_path = os.path.join(output_dir, "Volatility_Analysis.csv")
    volatility_df.to_csv(output_path, index=False)
    print(f"📊 Volatility analysis saved: {output_path}")

def calculate_cumulative_return(stock_data):
    """Calculate cumulative return for each stock."""
    cumulative_return_data = []
    
    for ticker, df in stock_data.items():
        if len(df) < 2:
            print(f"⚠️ Not enough data for {ticker} to calculate cumulative return.")
            continue
        first_close = df.iloc[0]["close"]
        last_close = df.iloc[-1]["close"]
        cumulative_return = ((last_close - first_close) / first_close) * 100
        cumulative_return_data.append({"Ticker": ticker, "Cumulative Return": cumulative_return})
    
    cumulative_df = pd.DataFrame(cumulative_return_data)
    cumulative_df.sort_values(by="Cumulative Return", ascending=False, inplace=True)
    output_path = os.path.join(output_dir, "Cumulative_Return_Analysis.csv")
    cumulative_df.to_csv(output_path, index=False)
    print(f"📊 Cumulative return analysis saved: {output_path}")
    
    return cumulative_df

def calculate_sector_average_yearly_return(cumulative_df):
    """Calculate sector-wise average yearly return."""
    sector_data = pd.read_csv(sector_file)
    sector_data["Symbol"] = sector_data["Symbol"].apply(lambda x: x.split(": ")[-1] if ": " in str(x) else x)
    
    cumulative_df["Ticker"] = cumulative_df["Ticker"].str.strip().str.upper()
    sector_data["Symbol"] = sector_data["Symbol"].str.strip().str.upper()
    
    merged_df = cumulative_df.merge(sector_data, left_on="Ticker", right_on="Symbol", how="left")
    sector_avg_return = merged_df.groupby("sector")["Cumulative Return"].mean().reset_index()
    sector_avg_return.rename(columns={"Cumulative Return": "Average Yearly Return (%)"}, inplace=True)
    
    output_path = os.path.join(output_dir, "Sector_Wise_Yearly_Return.csv")
    sector_avg_return.to_csv(output_path, index=False)
    print(f"📊 Sector-wise yearly return analysis saved: {output_path}")

def calculate_correlation(stock_data):
    """Calculate stock correlation matrix."""
    df = pd.DataFrame(stock_data)
    correlation_matrix = df.pct_change().corr()
    
    correlation_long = correlation_matrix.stack().reset_index()
    correlation_long.columns = ["Stock_1", "Stock_2", "Correlation"]
    
    output_path = os.path.join(output_dir, "Stock_Correlation_Long.csv")
    correlation_long.to_csv(output_path, index=False)
    print(f"📊 Correlation matrix saved: {output_path}")

def calculate_monthly_gainers_losers(stock_data):
    """Calculate top 5 gainers and losers per month."""
    all_data = []
    
    for ticker, df in stock_data.items():
        df["month"] = df["date"].dt.to_period("M")
        df["monthly_return"] = df["close"].pct_change() * 100
        monthly_returns = df.groupby("month")["monthly_return"].last().reset_index()
        monthly_returns["ticker"] = ticker
        all_data.append(monthly_returns)
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    top_gainers_losers = []
    for month, group in combined_df.groupby("month"):
        top_gainers = group.nlargest(5, "monthly_return").assign(category="Gainer")
        top_losers = group.nsmallest(5, "monthly_return").assign(category="Loser")
        top_gainers_losers.append(pd.concat([top_gainers, top_losers]))
    
    final_df = pd.concat(top_gainers_losers, ignore_index=True)
    output_path = os.path.join(output_dir, "Top_Gainers_Losers_Monthly.csv")
    final_df.to_csv(output_path, index=False)
    print(f"✅ Monthly top gainers and losers data saved: {output_path}")

def concatenate_nifty_50(stock_data):
    """Concatenate all 50 Nifty stock files into a single CSV without daily_return and monthly_return."""
    all_stocks = []
    
    for ticker, df in stock_data.items():
        df["Ticker"] = ticker  # Add stock identifier
        columns_to_keep = ["date", "open", "close", "high", "low", "volume", "month", "Ticker"]
        df = df[columns_to_keep]  # Keep only required columns
        all_stocks.append(df)
    
    if all_stocks:
        nifty_50_df = pd.concat(all_stocks, ignore_index=True)
        output_path = os.path.join(output_dir, "Nifty_50_Combined.csv")
        nifty_50_df.to_csv(output_path, index=False)
        print(f"📊 Nifty 50 combined dataset saved without daily_return and monthly_return: {output_path}")
    else:
        print("⚠️ No stock data available for Nifty 50 concatenation.")

def main():
    """Run all analysis functions sequentially."""
    stock_data = load_stock_data(input_dir)
    calculate_volatility(stock_data)
    cumulative_df = calculate_cumulative_return(stock_data)
    calculate_sector_average_yearly_return(cumulative_df)
    
    stock_close_data = load_stock_data(input_dir, only_close_prices=True)
    calculate_correlation(stock_close_data)
    calculate_monthly_gainers_losers(stock_data)
    
    concatenate_nifty_50(stock_data)  # New function to create Nifty 50 dataset
    
    print("🎯 All stock analysis completed successfully!")

if __name__ == "__main__":
    main()
