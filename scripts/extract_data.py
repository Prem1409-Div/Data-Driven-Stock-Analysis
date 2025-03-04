import os
import yaml
import pandas as pd
from pathlib import Path

# Define base directory (Update if needed)
base_dir = r"C:\Users\Premkumar.Nagendran\OneDrive - Agilisium Consulting India Private Limited\Mini Projects\Data-Driven Stock Analysis"

# Define where processed data will be saved
output_dir = os.path.join(base_dir, "processed_data", "individual_stocks")
os.makedirs(output_dir, exist_ok=True)

# Function to extract all YAML files recursively
def get_yaml_files(root_dir):
    yaml_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):  # Include both YAML extensions
                yaml_files.append(os.path.join(root, file))
    return yaml_files

# Function to process YAML files and extract stock data
def process_yaml_files(yaml_files):
    stock_data = {}

    for file in yaml_files:
        with open(file, "r", encoding="utf-8") as f:
            try:
                records = yaml.safe_load(f)  # Load YAML data

                # Ensure data is a list of dictionaries
                if isinstance(records, list):
                    for record in records:
                        ticker = record.get("Ticker", "UNKNOWN")
                        date = record.get("date")
                        open_price = record.get("open")
                        close_price = record.get("close")
                        high = record.get("high")
                        low = record.get("low")
                        volume = record.get("volume")
                        month = record.get("month")  # Can be used for additional organization

                        if ticker not in stock_data:
                            stock_data[ticker] = []

                        stock_data[ticker].append({
                            "date": date,
                            "open": open_price,
                            "close": close_price,
                            "high": high,
                            "low": low,
                            "volume": volume,
                            "month": month
                        })
            except Exception as e:
                print(f"⚠️ Error processing file {file}: {e}")

    return stock_data

# Function to save data as separate CSVs for each ticker
def save_to_csv(stock_data, output_dir):
    for ticker, records in stock_data.items():
        df = pd.DataFrame(records)
        df.sort_values(by="date", inplace=True)  # Sort by date for consistency
        output_file = Path(output_dir) / f"{ticker}.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Saved: {output_file}")

# Main function to run the extraction
def main():
    yaml_files = get_yaml_files(os.path.join(base_dir, "data", "data"))  # Adjust based on YAML structure
    print(f"🔍 Found {len(yaml_files)} YAML files.")

    stock_data = process_yaml_files(yaml_files)
    save_to_csv(stock_data, output_dir)

    print("🎯 Data extraction complete! Ready for analysis.")

# Run the script
if __name__ == "__main__":
    main()
