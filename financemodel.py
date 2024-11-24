import streamlit as st
import yfinance as yf
import pandas as pd
from stocknews import StockNews

st.title("Stock Dashboard")

# Ticker selection and date input
tickers = ('TSLA', 'AAPL', 'MSFT', 'BTC-USD', 'ETH-USD')
dropdown = st.multiselect('Pick your assets', tickers)
start = st.date_input("Start", value=pd.to_datetime('2024-01-01'))
end = st.date_input('End', value=pd.to_datetime('today'))
display_option = st.radio('Display', ('Price', 'Cumulative Return'))

# Relative return calculation
def relativeret(df):
    rel = df.pct_change()
    cumret = (1 + rel).cumprod() - 1
    cumret = cumret.fillna(0)
    return cumret

# Sidebar navigation
st.sidebar.success('Welcome to Stock Dashboard')
st.sidebar.header("Navigation")
page = st.sidebar.selectbox('Select a page', options=["Home", "News", "Price Movements", "Technical Indicators", "Financials"])
st.sidebar.info("""
        **Home Page Guide:**
        1. **Select Assets**: Choose assets from the dropdown.
        2. **Set Date Range**: Pick start and end dates.
        3. **Display Option**: Choose between 'Price' and 'Cumulative Return'.
        4. **View Data**: Line chart displays selected assets' price or cumulative return.
        """)
st.sidebar.info("""
        **News Page Guide:**
        1. **Select Asset**: Pick at least one asset on the Home page.
        2. **View News**: Displays latest news for the first selected asset.
        """)
st.sidebar.info("""
        **Price Movements Page Guide:**
        1. **Select Asset**: Pick at least one asset on the Home page.
        2. **View Price Movements**: Table shows price movements over the selected date range.
        """)
st.sidebar.info("""
        **Technical Indicators Page Guide:**
        1. **Select Asset**: Pick at least one asset on the Home page.
        2. **Moving Averages**:
            - Set short-term and long-term MA periods.
            - View price chart with moving averages.
        3. **RSI**: Set RSI period and view RSI chart.
        """)
st.sidebar.info("""
        **Financials Page Guide:**
        1. **Select Asset**: Pick at least one asset on the Home page.
        2. **View Financial Statements**:
            - **Balance Sheet**: Shows the company's balance sheet.
            - **Income Statement**: Displays the income statement.
            - **Cash Flow Statement**: Presents the cash flow statement.
        """)
st.sidebar.caption('Developed by Srishti Ventures')

# Home page
if page == "Home":
    st.header("Home")
    if dropdown:
        df = yf.download(dropdown, start, end)['Adj Close']
        if display_option == 'Cumulative Return':
            df = relativeret(df)
        st.line_chart(df)
    else:
        st.warning("Please select at least one asset to display data.")

# News page
elif page == "News":
    st.header("News")
    if dropdown:
        ticker = dropdown[0]  # Fetch news for the first selected ticker
        st.subheader(f"News for {ticker}")
        sn = StockNews(ticker, save_news=False)
        news = sn.read_rss()
        
        for i in range(5):
            st.subheader(f'News {i + 1}')
            st.info(news['title'][i])
            st.write(news['published'][i])
            st.subheader(news['summary'][i])
    else:
        st.warning("Please select at least one asset to see the news.")

# Price Movements page
elif page == "Price Movements":
    st.header("Price Movements")
    if dropdown:
        df = yf.download(dropdown, start, end)['Adj Close']
        st.write(df)
    else:
        st.warning("Please select at least one asset to see the price movements.")

# Technical Indicators page
elif page == "Technical Indicators":
    st.header("Technical Indicators")
    if dropdown:
        ticker = dropdown[0]  # Use the first selected ticker
        df_ticker = yf.download(ticker, start, end)['Adj Close']
        
        st.subheader("Moving Averages")
        ma_short = st.number_input("Short-term MA", min_value=1, value=10)
        ma_long = st.number_input("Long-term MA", min_value=1, value=50)
        
        ma_short_series = df_ticker.rolling(window=ma_short).mean()
        ma_long_series = df_ticker.rolling(window=ma_long).mean()
        
        st.line_chart(pd.DataFrame({'Price': df_ticker, f'{ma_short}-MA': ma_short_series, f'{ma_long}-MA': ma_long_series}))
        
        st.subheader("Relative Strength Index (RSI)")
        rsi_period = st.number_input("RSI Period", min_value=1, value=14)
        
        delta = df_ticker.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        st.line_chart(rsi)
    else:
        st.warning("Please select at least one asset to see the technical indicators.")

# Financials page
elif page == "Financials":
    st.header("Company Financials")
    if dropdown:
        ticker = dropdown[0]  # Use the first selected ticker
        ticker_info = yf.Ticker(ticker)
        
        st.subheader("Balance Sheet")
        balance_sheet = ticker_info.balance_sheet
        st.write(balance_sheet)
        
        st.subheader("Income Statement")
        income_stmt = ticker_info.financials
        st.write(income_stmt)
        
        st.subheader("Cash Flow Statement")
        cash_flow = ticker_info.cashflow
        st.write(cash_flow)
    else:
        st.warning("Please select at least one asset to see the financials.")
