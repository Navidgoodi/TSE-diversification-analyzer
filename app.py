import streamlit as st
import finpy_tse as tse
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
import jdatetime
import time

# --- Page Configuration ---
st.set_page_config(page_title="Diversification Analysis (Final Ver.)", layout="wide", page_icon="💰")

# Set LTR (Left-to-Right) layout for English
st.markdown("""
<style>
    .main { direction: ltr; text-align: left; font-family: 'Segoe UI', Tahoma, sans-serif; }
    h1, h2, h3, p, div, label, .stTextInput, .stTextArea { text-align: left !important; direction: ltr !important; }
    .stMarkdown { text-align: left !important; }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

def convert_jalali_to_gregorian(j_date_str):
    """
    Converts a Jalali date string to a Gregorian datetime object.
    Input format usually: 1400-01-01 or 1400/01/01
    """
    try:
        j_date_str = str(j_date_str).replace('/', '-')
        parts = j_date_str.split('-')
        if len(parts) == 3:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            return jdatetime.date(y, m, d).togregorian()
    except:
        return None
    return None

@st.cache_data(ttl=3600*12)
def fetch_tse_data_fixed(ticker_list, start_date_jalali):
    combined_data = pd.DataFrame()
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(ticker_list)
    
    logs = []
    
    # For debugging: Sample of raw data from the first successful stock
    sample_raw_data = None 

    for i, ticker in enumerate(ticker_list):
        ticker = ticker.strip()
        status_text.text(f"📥 Processing: {ticker} ...")
        
        try:
            # ignore_date=False is important to keep the date index
            df = tse.Get_Price_History(
                stock=ticker,
                start_date=start_date_jalali,
                adjust_price=True,
                show_weekday=False,
                double_date=True 
            )
            
            if df is not None and not df.empty:
                # 1. Reset index to access J-DATE
                df = df.reset_index()
                
                # Save sample data for user display (only for the first successful stock)
                if sample_raw_data is None:
                    sample_raw_data = df.head(3).to_dict()

                # 2. Find date column and convert to standard Gregorian
                # If 'Date' (Gregorian) exists, use it; otherwise convert 'J-DATE'
                if 'Date' in df.columns:
                    df['date_gregorian'] = pd.to_datetime(df['Date'])
                elif 'J-DATE' in df.columns:
                    df['date_gregorian'] = df['J-DATE'].apply(convert_jalali_to_gregorian)
                    df['date_gregorian'] = pd.to_datetime(df['date_gregorian'])
                else:
                    # Attempt to convert previous index if no column found
                    logs.append(f"⚠️ {ticker}: Date column not found (Columns: {list(df.columns)})")
                    continue

                # 3. Set final index
                df = df.set_index('date_gregorian')
                df = df.sort_index()
                
                # Remove duplicate dates in index
                df = df[~df.index.duplicated(keep='first')]

                # Select closing price column
                # Sometimes it is 'Close', 'Adj Close', or 'Final'
                price_col = None
                for col in ['Close', 'Adj Close', 'PDrCotVal', 'Final']:
                    if col in df.columns:
                        price_col = col
                        break
                
                if price_col:
                    series = df[price_col]
                    series.name = ticker
                    
                    # Condition for minimum data points (e.g., 30 days)
                    if len(series) > 30:
                        if combined_data.empty:
                            combined_data = pd.DataFrame(series)
                        else:
                            combined_data = combined_data.join(series, how='outer')
                        logs.append(f"✅ {ticker}: Fetched ({len(series)} days)")
                    else:
                        logs.append(f"⚠️ {ticker}: Insufficient data")
                else:
                    logs.append(f"⚠️ {ticker}: Price column not found")
            else:
                logs.append(f"❌ {ticker}: Empty data returned")
                
        except Exception as e:
            logs.append(f"❌ {ticker}: Error ({str(e)})")
            # Short pause to prevent blocking
            time.sleep(0.5)
            continue
        
        progress_bar.progress((i + 1) / total)
        
    status_text.empty()
    progress_bar.empty()
    
    return combined_data, logs, sample_raw_data

def calculate_portfolio_risk(returns, num_stocks, iterations):
    risks = []
    available_stocks = returns.columns.tolist()
    actual_num = min(num_stocks, len(available_stocks))
    
    for _ in range(iterations):
        selected = random.sample(available_stocks, actual_num)
        subset = returns[selected]
        # Mean calculation handling NaN (if a stock is closed on a day, mean of others is used)
        portfolio_ret = subset.mean(axis=1)
        risk = portfolio_ret.std() * np.sqrt(242) # Annualization (approx 242 trading days)
        risks.append(risk)
        
    return np.mean(risks)

# --- User Interface ---

st.title("📊 Diversification Effect Analysis")
st.write("In this tool, we fetch real data from the Tehran Stock Exchange (TSE) to demonstrate how adding stocks to a portfolio reduces risk.")

with st.sidebar:
    st.header("Parameters")
    
    # Default list (Must remain in Persian as API requires Persian names)
    default_symbols = "فولاد فملی خودرو وبملت شپنا شبندر پارسان وغدیر اخابر همراه حکشتی کگل کچاد رمپنا شتران فارس خساپا وتجارت وبصادر تاپیکو"
    input_tickers = st.text_area("Stock Tickers (Space separated)", value=default_symbols, height=150)
    ticker_list = input_tickers.split()
    
    start_year = st.selectbox("Data Start Year (Jalali):", [1402, 1401, 1400, 1399, 1398], index=2)
    start_date_str = f"{start_year}-01-01"
    
    iterations = st.slider("Simulation Iterations (Accuracy)", 50, 500, 100)
    max_portfolio_size = st.slider("Max Portfolio Size", 2, 20, 15)
    
    run_btn = st.button("🚀 Run Analysis")

if run_btn:
    # 1. Fetch Data
    df_prices, logs, sample_debug = fetch_tse_data_fixed(ticker_list, start_date_str)
    
    # Show logs in Expander
    with st.expander("📝 Data Fetching Status Log", expanded=False):
        st.write(logs)
        if sample_debug:
            st.write("Raw Data Sample (For column inspection):")
            st.write(sample_debug)
    
    if df_prices.empty:
        st.error("❌ No usable data fetched! Please change the ticker list or check your internet connection.")
    else:
        # 2. Data Cleaning
        # Filling missing data (Forward Fill) - Crucial for TSE where symbols stop frequently
        df_filled = df_prices.ffill()
        
        # Calculate daily returns
        daily_returns = df_filled.pct_change()
        
        # Drop days where market was completely closed (all NaN)
        daily_returns = daily_returns.dropna(how='all')
        
        num_stocks = len(daily_returns.columns)
        st.success(f"✅ Successfully processed {num_stocks} stocks.")
        
        if num_stocks < 2:
            st.warning("⚠️ Not enough stocks. At least 2 stocks are required.")
        else:
            # 3. Calculation Loop
            x_data, y_data = [], []
            limit_n = min(max_portfolio_size, num_stocks)
            
            my_bar = st.progress(0)
            
            for n in range(1, limit_n + 1):
                risk = calculate_portfolio_risk(daily_returns, n, iterations)
                x_data.append(n)
                y_data.append(risk)
                my_bar.progress(n / limit_n)
                
            my_bar.empty()
            
            # 4. Plotting
            fig = go.Figure()
            
            # Main curve
            fig.add_trace(go.Scatter(
                x=x_data, y=y_data,
                mode='lines+markers',
                name='Portfolio Risk',
                line=dict(color='#00ADB5', width=4),
                marker=dict(size=10, color='white', line=dict(width=2, color='#00ADB5'))
            ))
            
            # Asymptote line (Approximate Systematic Risk)
            sys_risk = y_data[-1]
            fig.add_hline(y=sys_risk, line_dash="dot", annotation_text="Systematic Risk (Unavoidable)", 
                          annotation_position="bottom right", line_color="orange")

            fig.update_layout(
                title="<b>Effect of Diversification on Risk Reduction (TSE)</b>",
                xaxis_title="Number of Stocks in Portfolio",
                yaxis_title="Annual Standard Deviation (Risk)",
                template="plotly_dark",
                height=550,
                hovermode="x"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 5. Insight
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🔹 Single Stock Risk (Avg): **{y_data[0]:.2f}**")
            with col2:
                risk_drop = ((y_data[0] - sys_risk) / y_data[0]) * 100
                st.success(f"📉 Risk Reduction with {limit_n} stocks: **{risk_drop:.1f}%**")
