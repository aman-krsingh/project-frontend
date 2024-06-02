import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from stocknews import StockNews
import requests
from datetime import datetime, timedelta


# fetching data from backed
def fetch_data_from_api(ticker):
    url = f'https://functionapp456.azurewebsites.net/api/pred_{ticker}?code={code}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data for {ticker}. Status code: {response.status_code}")

# ploting the data we get from backed
def plot_data(data):
    if data is None:
        return

    hist_with_pred_value = data["hist_with_pred_value"]
    hist_value = data["hist_value"]

    fig = go.Figure()

    # Plot historical values with prediction
    fig.add_trace(go.Scatter(
        x=list(range(len(hist_with_pred_value))),
        y=hist_with_pred_value,
        mode='lines',
        name='Predicted close',
        line=dict(color='red')
    ))

    # Plot historical values
    fig.add_trace(go.Scatter(
        x=list(range(len(hist_value))),
        y=hist_value,
        mode='lines',
        name='Historical close',
        line=dict(color='blue')
    ))

    fig.update_layout(
        title='Historical and Predicted Stock Prices',
        xaxis_title='Days',
        yaxis_title='Close',
        xaxis=dict(showticklabels=False)
    )

    st.plotly_chart(fig, use_container_width=True)

# future 30 days prediction value table
def show_prediction_table(data, days=30):
    if data is None:
        return
    
    hist_with_pred_value = data["hist_with_pred_value"]
    start_date = datetime.today() + timedelta(days=1)
    dates = [start_date + timedelta(days=i) for i in range(days)]

    # Create DataFrame for the table
    prediction_df = pd.DataFrame({
        "Date": dates,
        "Closing Price": hist_with_pred_value[-days:]  # Take the last `days` values from prediction
    })

    
    prediction_df.index = prediction_df.index + 1

    st.write("### Prediction for the Next 30 Days")
    st.dataframe(prediction_df, use_container_width=True)

# news card layout
def render_news_section(ticker):
    st.write(f"<p class='big2-font'>Top News related to {ticker}</p>", unsafe_allow_html=True)
    sn = StockNews(ticker, save_news=False)
    news = sn.read_rss()
    
    num_news = min(len(news['title']), 8) # upto 6 news items

    # CSS for cards
    st.markdown("""
    <style>
    .news-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: space-between;
    }

    .news-card {
        background-color: #543310;
        padding: 20px;
        border-radius: 5px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-bottom: 40px; /* Corrected space in margin-bottom */
        flex: 1 1 calc(33.333% - 20px); /* Adjust width for three columns with gap */
    }

    .news-title {
        font-size: 14px;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Create a container for the news cards
    st.markdown('<div class="news-container">', unsafe_allow_html=True)
    
    for i in range(num_news):
        title = news['title'][i]
        summary = news['summary'][i]

        st.markdown(
            f"""
            <div class="news-card">
                <p class="news-title">{title}</p>
                <p>{summary}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)


st.set_page_config(page_title="Stock prices", page_icon="chart_with_upwards_trend", layout="wide")
def render_dashboard_page():
    st.title("Stock Prediction Dashboard")

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    local_css("style/style.css")

    def predict(ticker, days=30):  
     with st.spinner("Predicting..."):
      
        data = fetch_data_from_api(st.session_state.ticker)
        if data:
            show_prediction_table(data,days)
            plot_data(data)


    if 'session_state' not in st.session_state:
        st.session_state.ticker = None

    col1, col2 = st.columns(2)

    with col1:
        ticker_options = ['PAYTM', 'GOOG','AAPL','META','TCS',]
        ticker = st.session_state.ticker or ticker_options[0]
        st.session_state.ticker = st.selectbox(label="Choose a ticker", options=ticker_options, help='Please select a ticker from the dropdown.')

    with col2:
        submit_button = st.button("Submit")

    if submit_button:
        if st.session_state.ticker not in ticker_options:        
            st.warning("Please select a valid ticker from the dropdown.")
        else:
            st.markdown("""
                <style>
                .big2-font {
                    font-size: 25px;
                    text-align: center;
                    margin-bottom: 20px;
                }
                .centered-dataframe {
                    display: flex;
                    justify-content: center;
                }
                </style>
                """, unsafe_allow_html=True)
            prediction, News= st.tabs(['Prediction', 'Top News'])

            
            with prediction:
                st.markdown("""
                        <style>
                        .big3-font {
                            font-size: 10px;
                            text-align: center;
                            margin-bottom: 20px;
                        }
                        .centered-dataframe {
                            display: flex;
                            justify-content: center;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                st.write(f"<p class='big2-font'>Future 30 Days Forecast for {st.session_state.ticker}</p>", unsafe_allow_html=True)
                predict(st.session_state.ticker, 30) 
    
           
            with News:
                render_news_section(st.session_state.ticker)
                

            
