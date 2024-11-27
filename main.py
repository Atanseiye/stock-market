import yfinance as yf
import json
import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
import plotly.graph_objects as go


openai_client = ChatOpenAI()
class Agent:

    def __init__(self):
        pass

    def texts(query):
        text = f'''You are an AI assistance developed to assist with extracting information
                   from a given text and you return a json. Give the text: {query} etract the following
                   1. the action. eg: buy, sell
                   2. amount. eg: 1000
                   3. shares. eg: Barclays
                   4. when. eg: above average. 
                   5. time. eg: over last week. NOTE: Ensure to convert the time to normal standard datetime range in yahoofinance eg 1mo for past one month, While a week represent 5day therefore over last week means 5d. Ensure to do your calculations where necessary.
                   6. days_count. eg: 7 days. The 7 days was gotten by counting how many days that are in step 4 above.
                   Always lookup the symbol for the shares and replace the name with the symbol. like BARC for Barclays.
                   Create a key-value pair to save the json. the key should be named - results'''
        return text

    def extract(text):
        return openai_client.invoke(text).content

query = 'Buy 500 Apple shares when the Value is Above average over last one month, and sell 1000 Barclays shares when the Value is Below average over previous week. Show me results over the last 3 months'

# What every algorithm will have
def wrangle(data):
    data = data.dropna()

    return data

ticker_symbol = 'AAPL'
def fetch_data(query):
    agent = Agent.extract(Agent.texts(query))
    data = json.loads(agent)
    print(data)
    buy_ticker_symbol, buy_period = data['results'][0]['shares'], data['results'][0]['time']
    ticker = yf.Ticker(buy_ticker_symbol)
    historical_data = ticker.history(period=buy_period)
    dataframe = pd.DataFrame(historical_data)
    dataframe = wrangle(dataframe)

    # process day_count
    day_count = int(data['results'][0]['days_count'].split(' ')[0])
    print(buy_ticker_symbol, buy_period, day_count)

    # Calculate the 2-week moving average (10 trading days)
    dataframe['2_week_avg'] = dataframe['Close'].rolling(window=2).mean()

    # Identify days where the Close price is above the 2-week average
    dataframe['Buy_Signal'] = dataframe['Close'] > dataframe['2_week_avg']


    return dataframe


def plot_data(dataframe):
    # Create a Plotly figure
    fig = go.Figure()

    # Add Close price to the plot
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['Close'],
                             mode='lines', name='Close Price'))

    # Add 2-week moving average to the plot
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe['2_week_avg'],
                             mode='lines', name='2 Week Moving Avg', line=dict(dash='dot', color='red')))

    # Update layout
    fig.update_layout(title="Stock Price with 2-Week Moving Average",
                      xaxis_title="Date",
                      yaxis_title="Price (USD)",
                      legend_title="Legend",
                      template="plotly_white")

    return fig

# print(fetch_data(query))


query = st.text_input('Pass your query here')

pull = st.button('Query')
if pull:
    result = fetch_data(query)
    st.write(result)

    # Generate and display the Plotly chart
    fig = plot_data(result)
    st.plotly_chart(fig)