import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
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
tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "🔍 Sector Breakdown", "🔥 Heatmap Analysis", "📈 Monthly Performance"])

with tab1:  # Market Overview Tab
    # Fetch data from MySQL
# 1. Green vs Red Stocks

    green_red_query = """
    SELECT 
        SUM(CASE WHEN latest_data.`close` > latest_data.`open` THEN 1 ELSE 0 END) AS Green_Stocks,
        SUM(CASE WHEN latest_data.`close` <= latest_data.`open` THEN 1 ELSE 0 END) AS Red_Stocks
    FROM (
        SELECT a.Ticker, a.`open`, a.`close`
        FROM nifty_50_combined a
        INNER JOIN (
            SELECT Ticker, MAX(date) AS max_date
            FROM nifty_50_combined
            GROUP BY Ticker
        ) b ON a.Ticker = b.Ticker AND a.date = b.max_date
    ) latest_data
"""
    green_red = get_data_from_sql(green_red_query)

# 2. Average Price & Volume per Stock (All Time)
    avg_per_stock_query = """
    SELECT 
        Ticker,
        AVG(`close`) AS Avg_Price,
        AVG(`volume`) AS Avg_Volume
    FROM nifty_50_combined
    GROUP BY Ticker
    ORDER BY Ticker
""" 
    avg_per_stock = get_data_from_sql(avg_per_stock_query)

    # # Display DataFrames
    # col1, col2 = st.columns(2)
   
    # with col1:
    #     st.subheader("🏆 Top 10 Performing Sectors")
    #     st.dataframe(top_green_sectors.style.format({'Average_Yearly_Return_(%)': '{:.2f}%'}))

    # with col2:
    #     st.subheader("📉 Top 10 Underperforming Sectors")
    #     st.dataframe(top_loss_sectors.style.format({'Average_Yearly_Return_(%)': '{:.2f}%'}))

    # Market Summary
    st.subheader("📈 Market Summary")
    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.metric("🟢 Green Stocks (Today)", green_red['Green_Stocks'][0])


    with col2:
        st.metric("🔴 Red Stocks (Today)", green_red['Red_Stocks'][0])


    # Display Average Table
    st.subheader("📊Averages per Stock")
    st.dataframe(
        avg_per_stock.style.format({
            'Avg_Price': '₹{:.2f}',
            'Avg_Volume': '{:,.0f}'
        }),
        use_container_width=True,
        height=600
    ) 

    # Performance Leaders Section
    st.subheader("📈 Stock Performance Leaders")
    col_top, col_bottom = st.columns(2)

    # Top 10 Green Stocks
    with col_top:
        top_green_query = """
            SELECT Ticker, `Average_Yearly_Return_(%)` 
            FROM sector_ticker_wise_yearly_return
            ORDER BY `Average_Yearly_Return_(%)` DESC 
            LIMIT 10
        """
        top_green = get_data_from_sql(top_green_query)

        st.markdown("### 🥇 Top 10 Gainers")
        st.dataframe(
             top_green.rename(columns={'Average_Yearly_Return_(%)': 'Return (%)'})
                .style
                .format({'Return (%)': '{:.2f}%'})
                .applymap(lambda x: 'color: #2ecc71' if x > 0 else '', 
                        subset=['Return (%)'])
                .set_properties(**{'text-align': 'left'}),
            use_container_width=True,
            height=400
        )
        

    # Top 10 Loss Stocks
    with col_bottom:
        top_loss_query = """
            SELECT Ticker, `Average_Yearly_Return_(%)` 
            FROM sector_ticker_wise_yearly_return
            ORDER BY `Average_Yearly_Return_(%)` ASC 
            LIMIT 10
        """
        top_loss = get_data_from_sql(top_loss_query)

        st.markdown("### 🥈 Top 10 Losers")
        st.dataframe(
            top_loss.rename(columns={'Average_Yearly_Return_(%)': 'Return (%)'})
                .style
                .format({'Return (%)': '{:.2f}%'})
                .applymap(lambda x: 'color: #e74c3c' if x < 0 else '', 
                        subset=['Return (%)'])
                .set_properties(**{'text-align': 'left'}),
            use_container_width=True,
            height=400
        )



    # Visualization: Volatility Analysis
    st.subheader("📉 Volatility Analysis")
    query_volatility = """
        SELECT Ticker, Yearly_Volatility
        FROM volatility_analysis
        ORDER BY Yearly_Volatility DESC
        LIMIT 10
    """
    volatility_data = get_data_from_sql(query_volatility)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = sns.barplot(y=volatility_data["Ticker"],
                      x=volatility_data["Yearly_Volatility"],
                      palette="coolwarm", ax=ax)
    
    # Add value labels
    max_volatility = volatility_data["Yearly_Volatility"].max()
    for bar in bars.patches:
        width = bar.get_width()
        label_x = width - (max_volatility * 0.01)  # Adjust position based on max value
        label_y = bar.get_y() + bar.get_height()/2
        ax.text(label_x, label_y, 
               f'{width:.2f}',
               va='center', ha='right', color='white')
    
    ax.set_xlabel("Volatility Index", fontsize=12)
    ax.set_ylabel("Stock Ticker", fontsize=12)
    ax.set_title("Top 10 Most Volatile Stocks", fontsize=14)
    st.pyplot(fig)

    # Visualization: Sector-wise Performance
    st.subheader("📌 Sector-wise Performance")
    query_sector = "SELECT sector, `Average_Yearly_Return_(%)` FROM sector_wise_yearly_return"
    sector_data = get_data_from_sql(query_sector)

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = sns.barplot(y=sector_data["sector"],
                      x=sector_data["Average_Yearly_Return_(%)"],
                      palette="viridis", ax=ax)
    
    # Add value labels with dynamic positioning
    max_return = sector_data["Average_Yearly_Return_(%)"].abs().max()
    for bar in bars.patches:
        width = bar.get_width()
        offset = max_return * 0.02  # 2% of max value for padding
        label_x = width - offset if width > 0 else width + offset
        label_y = bar.get_y() + bar.get_height()/2
        color = 'white' if width > 0 else 'black'
        
        ax.text(label_x, label_y, 
               f'{width:.2f}%',
               va='center', 
               ha='right' if width > 0 else 'left', 
               color=color)
    
    ax.set_xlabel("Average Return (%)", fontsize=12)
    ax.set_ylabel("Sector", fontsize=12)
    ax.set_title("Yearly Returns by Sector", fontsize=14)
    st.pyplot(fig)

with tab2:  # Sector Breakdown
    st.subheader("🔍 Sector Breakdown")

    # Fetch sector breakdown data
    break_down_query = "SELECT Ticker, sector, `Average_Yearly_Return_(%)` FROM sector_ticker_wise_yearly_return"
    break_down_sector_data = get_data_from_sql(break_down_query)

    if not break_down_sector_data.empty:
        col1, col2 = st.columns([1, 3])

        with col1:
            sectors = ["All"] + sorted(break_down_sector_data["sector"].dropna().unique().tolist())
            selected_sector = st.selectbox("Select Sector", sectors)

        filtered_data = break_down_sector_data if selected_sector == "All" else break_down_sector_data[break_down_sector_data["sector"] == selected_sector]

        with col2:
            if not filtered_data.empty:
                chart = alt.Chart(filtered_data).mark_bar().encode(
                    x=alt.X("Average_Yearly_Return_(%):Q", title="Average Yearly Return (%)"),
                    y=alt.Y("Ticker:N", sort="-x", title="Ticker"),
                    tooltip=["Ticker", "Average_Yearly_Return_(%)"]
                ).properties(
                    title="Average Yearly Return (%) by Ticker",
                    width=600
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning("No data available for the selected sector.")

with tab3:  # Heatmap Tab
    st.subheader("📊 Stock Correlation Matrix")
   
    query_correlation = "SELECT Stock_1, Stock_2, Correlation FROM stock_correlation_long"
    correlation_data = get_data_from_sql(query_correlation)

    if not correlation_data.empty:
        pivot_table = correlation_data.pivot(index="Stock_1",
                                           columns="Stock_2",
                                           values="Correlation")
       
        fig, ax = plt.subplots(figsize=(24, 20))
        
        # Enhanced heatmap with annotations and better coloring
        sns.heatmap(
            pivot_table,
            cmap="coolwarm",
            linewidths=0.1,
            ax=ax,
            annot=True,  # Show values
            annot_kws={"size": 8},  # Annotation font size
            fmt=".2f",  # Format to 2 decimal places
            cbar_kws={'shrink': 0.8, 'label': 'Correlation Scale'},
            vmin=-1,  # Fixed scale for better color interpretation
            vmax=1,
            center=0  # Neutral point at zero correlation
        )
        
        # Improved labels and titles
        ax.set_title("Stock Price Correlation Heatmap", fontsize=18, pad=20)
        ax.set_xlabel("Stock Tickers", fontsize=14)
        ax.set_ylabel("Stock Tickers", fontsize=14)
        
        # Rotate tick labels for better readability
        plt.xticks(
            rotation=45,
            horizontalalignment='right',
            fontsize=10
        )
        plt.yticks(fontsize=10)
        
        # Add grid lines for better cell distinction
        ax.grid(False)
        for _, spine in ax.spines.items():
            spine.set_visible(True)
            spine.set_color('black')
            
        st.pyplot(fig)
    else:
        st.warning("No correlation data available")

with tab4:  # Monthly Performance Tab
    st.subheader("📆 Monthly Stock Performance Analysis")
   
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
                st.stop()

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
                                bars = sns.barplot(x="monthly_return", y="ticker",
                                                 data=gainers, palette="Greens_d")
                                
                                # Add value labels
                                max_return = gainers["monthly_return"].max()
                                for bar in bars.patches:
                                    width = bar.get_width()
                                    label_x = width - (max_return * 0.03)
                                    label_y = bar.get_y() + bar.get_height()/2
                                    bars.text(label_x, label_y,
                                            f'{width:.2f}%',
                                            va='center', ha='right', color='white')
                                
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
                                bars = sns.barplot(x="monthly_return", y="ticker",
                                                 data=losers, palette="Reds_d")
                                
                                # Add value labels
                                min_return = losers["monthly_return"].min()
                                for bar in bars.patches:
                                    width = bar.get_width()
                                    label_x = width + (abs(min_return) * 0.03)
                                    label_y = bar.get_y() + bar.get_height()/2
                                    bars.text(label_x, label_y,
                                            f'{width:.2f}%',
                                            va='center', ha='left', color='white')
                                
                                ax.set_xlabel("Monthly Return (%)")
                                ax.set_ylabel("")
                                st.pyplot(fig)
                            else:
                                st.warning(f"No losers found for {month_year}")
                    else:
                        st.warning(f"No valid records found for {month_year}")

        else:
            st.warning("No monthly performance data found in database")

    except Exception as e:
        st.error(f"Database Error: {str(e)}")
