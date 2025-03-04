import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text

# Database connection setup
db_credentials = {
    "username": "root",
    "password": "Guvi%40003",
    "host": "localhost",
    "database": "Stock_Analysis_DB"
}

def get_data_from_sql(query, params=None):
    """Fetch data from MySQL using SQLAlchemy."""
    engine = create_engine(f"mysql+pymysql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}/{db_credentials['database']}")
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection, params=params)

# Streamlit UI setup
st.title("📈 Stock Market Analysis Dashboard")

# Main page sections
tab1, tab2, tab3 = st.tabs(["📊 Market Overview", "🔥 Heatmap Analysis", "📈 Monthly Performance"])

with tab1:  # Market Overview Tab
    # Fetch data from MySQL
    query_top_green_sectors = """
        SELECT sector, `Average_Yearly_Return_(%)` 
        FROM sector_wise_yearly_return 
        ORDER BY `Average_Yearly_Return_(%)` DESC 
        LIMIT 10
    """
    query_top_loss_sectors = """
        SELECT sector, `Average_Yearly_Return_(%)` 
        FROM sector_wise_yearly_return 
        ORDER BY `Average_Yearly_Return_(%)` ASC 
        LIMIT 10
    """
    query_market_summary = """
        SELECT 
            SUM(CASE WHEN `Average_Yearly_Return_(%)` > 0 THEN 1 ELSE 0 END) AS Green_Sectors,
            SUM(CASE WHEN `Average_Yearly_Return_(%)` <= 0 THEN 1 ELSE 0 END) AS Red_Sectors
        FROM sector_wise_yearly_return
    """

    top_green_sectors = get_data_from_sql(query_top_green_sectors)
    top_loss_sectors = get_data_from_sql(query_top_loss_sectors)
    market_summary = get_data_from_sql(query_market_summary)

    # Display DataFrames
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Performing Sectors")
        st.dataframe(top_green_sectors.style.format({'Average_Yearly_Return_(%)': '{:.2f}%'}))

    with col2:
        st.subheader("📉 Top 10 Underperforming Sectors")
        st.dataframe(top_loss_sectors.style.format({'Average_Yearly_Return_(%)': '{:.2f}%'}))

    # Market Summary
    st.subheader("📈 Market Summary")
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.metric(label="Green Sectors", value=market_summary['Green_Sectors'][0])
        
    with summary_col2:
        st.metric(label="Red Sectors", value=market_summary['Red_Sectors'][0])

    # Visualization: Volatility Analysis
    st.subheader("📉 Volatility Analysis")
    query_volatility = """
        SELECT Ticker, `Yearly_Volatility` 
        FROM volatility_analysis 
        ORDER BY `Yearly_Volatility` DESC 
        LIMIT 10
    """
    volatility_data = get_data_from_sql(query_volatility)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(y=volatility_data["Ticker"], 
                x=volatility_data["Yearly_Volatility"], 
                palette="coolwarm", ax=ax)
    ax.set_xlabel("Volatility Index", fontsize=12)
    ax.set_ylabel("Stock Ticker", fontsize=12)
    ax.set_title("Top 10 Most Volatile Stocks", fontsize=14)
    st.pyplot(fig)

    # Visualization: Sector-wise Performance
    st.subheader("📌 Sector-wise Performance")
    query_sector = "SELECT sector, `Average_Yearly_Return_(%)` FROM sector_wise_yearly_return"
    sector_data = get_data_from_sql(query_sector)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(y=sector_data["sector"], 
                x=sector_data["Average_Yearly_Return_(%)"], 
                palette="viridis", ax=ax)
    ax.set_xlabel("Average Return (%)", fontsize=12)
    ax.set_ylabel("Sector", fontsize=12)
    ax.set_title("Yearly Returns by Sector", fontsize=14)
    st.pyplot(fig)

with tab2:  # Heatmap Tab
    st.subheader("📊 Stock Correlation Matrix")
    
    query_correlation = "SELECT Stock_1, Stock_2, Correlation FROM stock_correlation_long"
    correlation_data = get_data_from_sql(query_correlation)

    if not correlation_data.empty:
        pivot_table = correlation_data.pivot(index="Stock_1", 
                                           columns="Stock_2", 
                                           values="Correlation")
        
        fig, ax = plt.subplots(figsize=(24, 20))
        sns.heatmap(pivot_table, cmap="coolwarm", 
                  linewidths=0.1, ax=ax, 
                  cbar_kws={'shrink': 0.8})
        ax.set_title("Stock Price Correlation Heatmap", fontsize=16)
        plt.xticks(fontsize=8, rotation=90)
        plt.yticks(fontsize=8)
        st.pyplot(fig)
    else:
        st.warning("No correlation data available")

with tab3:  # Monthly Performance Tab
    st.subheader("📆 Monthly Stock Performance Analysis")
    
    # with st.expander("🔍 View Raw Data Structure", expanded=False):
    #     st.markdown("**Database Schema:**")
    #     st.code("""
    #     Table: top_gainers_losers_monthly
    #     Columns:
    #     - month (text): Date in YYYY-MM format
    #     - monthly_return (float): Return percentage
    #     - ticker (text): Stock ticker symbols
    #     - category (text): 'Gainer' or 'Loser'
    #     """)
        
    #     raw_data = get_data_from_sql("SELECT * FROM top_gainers_losers_monthly LIMIT 5")
    #     st.write("Sample Data Preview:", raw_data)

    query_gainers_losers = """
        SELECT 
            month,
            ticker,
            monthly_return,
            TRIM(LOWER(category)) AS clean_category
        FROM top_gainers_losers_monthly
    """
    
    try:
        gainers_losers_data = get_data_from_sql(query_gainers_losers)
        
        if not gainers_losers_data.empty:
            # Convert YYYY-MM to datetime and extract year-month
            try:
                gainers_losers_data['date'] = pd.to_datetime(
                    gainers_losers_data['month'], 
                    format='%Y-%m'
                )
                gainers_losers_data['month_year'] = gainers_losers_data['date'].dt.strftime('%B %Y')
                gainers_losers_data['month'] = gainers_losers_data['date'].dt.month_name()
                gainers_losers_data['year'] = gainers_losers_data['date'].dt.year
            except Exception as date_error:
                st.error(f"Date parsing error: {str(date_error)}")
                st.write("Ensure month column contains valid YYYY-MM format")
                st.stop()

            # Sort by date and get unique month-year combinations
            gainers_losers_data = gainers_losers_data.sort_values('date')
            unique_months = gainers_losers_data['month_year'].unique()

            for month_year in unique_months:
                with st.expander(f"{month_year}", expanded=False):
                    month_data = gainers_losers_data[
                        (gainers_losers_data["month_year"] == month_year) &
                        (gainers_losers_data["clean_category"].isin(['gainer', 'loser']))
                    ]
                    
                    if not month_data.empty:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader(f"🏆 Top Gainers - {month_year}")
                            gainers = month_data[month_data["clean_category"] == 'gainer'].head(5)
                            if not gainers.empty:
                                fig, ax = plt.subplots(figsize=(10, 4))
                                sns.barplot(x="monthly_return", y="ticker",
                                          data=gainers, palette="Greens_d")
                                ax.set_xlabel("Monthly Return (%)")
                                ax.set_ylabel("Ticker")
                                st.pyplot(fig)
                            else:
                                st.warning(f"No gainers found for {month_year}")
                        
                        with col2:
                            st.subheader(f"📉 Top Losers - {month_year}")
                            losers = month_data[month_data["clean_category"] == 'loser'].head(5)
                            if not losers.empty:
                                fig, ax = plt.subplots(figsize=(10, 4))
                                sns.barplot(x="monthly_return", y="ticker",
                                          data=losers, palette="Reds_d")
                                ax.set_xlabel("Monthly Return (%)")
                                ax.set_ylabel("")
                                st.pyplot(fig)
                            else:
                                st.warning(f"No losers found for {month_year}")
                    else:
                        st.warning(f"No valid records found for {month_year}")
            
            # Show missing months from current year
            current_year = pd.Timestamp.now().year
            all_months = [pd.Timestamp(f'{current_year}-{m}-1').strftime('%B %Y') 
                         for m in range(1, 13)]
            missing_months = [m for m in all_months if m not in unique_months]
            
            if missing_months:
                st.info(f"Months with no data in {current_year}: {', '.join(missing_months)}")

        else:
            st.warning("No monthly performance data found in database")

    except Exception as e:
        st.error(f"Database Error: {str(e)}")
        st.markdown("**Common Solutions:**")
        st.write("1. Verify table contains data with valid YYYY-MM format")
        st.write("2. Check category values are either 'Gainer' or 'Loser'")
        st.write("3. Ensure database connection is active")