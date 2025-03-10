# Data-Driven Stock Analysis: Organizing, Cleaning, and Visualizing Market Trends

## Skills Takeaway From This Project
- Pandas
- Python
- Power BI
- Streamlit
- SQL
- Statistics
- Data Organizing, Cleaning, and Visualization

## Domain
Finance / Data Analytics

## Problem Statement
The Stock Performance Dashboard aims to provide a comprehensive visualization and analysis of Nifty 50 stocks' performance over the past year. This project analyzes daily stock data, including open, close, high, low, and volume values. It cleans and processes the data, generates key performance insights, and visualizes the top-performing stocks in terms of price changes and average stock metrics. The solution offers interactive dashboards using Streamlit and Power BI, helping investors, analysts, and enthusiasts make informed decisions based on stock performance trends.

## Business Use Cases
- **Stock Performance Ranking**: Identify the top 10 best-performing stocks (green stocks) and the top 10 worst-performing stocks (red stocks) over the past year.
- **Market Overview**: Provide an overall market summary with average stock performance and insights into the percentage of green vs. red stocks.
- **Investment Insights**: Help investors quickly identify which stocks showed consistent growth and which ones had significant declines.
- **Decision Support**: Provide insights on average prices, volatility, and overall stock behavior, useful for both retail and institutional traders.

## Project Folder Structure
```
Data-Driven Stock Analysis
│── data                     # Stores YAML files for stock data
│── processed_data           # Stores processed data and visualizations
│   ├── individual_stocks     # Extracted individual stock CSVs
│   ├── visualization_data    # CSVs for visualization
│   └── Sector_data.csv       # Sector-wise stock mapping
│── powerbi                  # Power BI dashboard file
│── scripts                  # Python scripts for data processing and analysis
│   ├── analysis.py           # Runs all functions sequentially
│   ├── extract_data.py       # Extracts stock data from YAML files
│   ├── load_to_sql.py        # Loads processed data into MySQL
└── run_pipeline.py   # This script
│   ├── streamlit_app.py      # Displays stock analysis results in Streamlit
```

## Approach
### 1. Data Extraction and Transformation
- Data is provided in YAML format, organized by months.
- Each month's folder contains date-wise data entries.
- Extract the data from YAML and transform it into CSV format, organized by stock symbols.
- After extraction, 50 CSV files are created (one for each stock symbol).

### 2. Data Analysis and Visualization Requirements
#### **Python DataFrame Metrics:**
- **Top 10 Green Stocks:** Sorted by yearly return (highest to lowest).
- **Top 10 Loss Stocks:** Sorted by yearly return (lowest to highest).
- **Market Summary:**
  - Number of green vs. red stocks
  - Average stock price
  - Average trading volume

#### **Key Visualizations:**
1. **Volatility Analysis**
   - **Objective**: Measure stock price fluctuations to assess risk.
   - **Metric**: Standard deviation of daily returns.
   - **Visualization**: Bar chart showing the top 10 most volatile stocks.

2. **Cumulative Return Over Time**
   - **Objective**: Show stock performance from the beginning to the end of the year.
   - **Metric**: Cumulative sum of daily returns.
   - **Visualization**: Line chart for the top 5 performing stocks.

3. **Sector-wise Performance**
   - **Objective**: Analyze stock performance based on industry sectors.
   - **Metric**: Average yearly return per sector.
   - **Visualization**: Bar chart displaying the average return by sector.

4. **Stock Price Correlation**
   - **Objective**: Identify relationships between different stocks.
   - **Metric**: Correlation matrix using closing prices.
   - **Visualization**: Heatmap showing correlation levels among stocks.

5. **Top 5 Gainers & Losers (Month-wise)**
   - **Objective**: Provide insights into the best and worst-performing stocks per month.
   - **Metric**: Monthly return percentage for each stock.
   - **Visualization**: 12 bar charts (one per month) displaying top gainers and losers.

## Dataset
Stock data is extracted from YAML files and stored in a structured format for analysis.

## Results
- A fully functional dashboard showcasing stock performance over the last year.
- Clear insights into market trends and stock behavior.
- Interactive visualizations using Power BI and Streamlit for easy data exploration.

## Technical Tags
- **Languages**: Python
- **Database**: MySQL
- **Visualization Tools**: Streamlit, Power BI
- **Libraries**: Pandas, Matplotlib, SQLAlchemy

## Project Deliverables
- **SQL Database**: Stores clean and processed stock data.
- **Python Scripts**: Handles data extraction, transformation, analysis, and visualization.
- **Power BI Dashboard**: Provides interactive stock performance insights.
- **Streamlit Application**: Offers a real-time interactive dashboard for stock analysis.

---

### How to Run the Project
#### **Step 1: Data Extraction**
```bash
python scripts/extract_data.py
```
Extracts stock data from YAML files and saves them as CSVs.

#### **Step 2: Load Data into MySQL**
```bash
python scripts/load_to_sql.py
```
Processes and loads extracted data into the MySQL database.

#### **Step 3: Run Analysis and Generate Metrics**
```bash
python scripts/analysis.py
```
Computes yearly returns, volatility, correlation, and other metrics.

#### **Step 4: Run Streamlit Application**
```bash
streamlit run scripts/streamlit_app.py
```
Launches an interactive dashboard to explore stock trends and insights.

---



