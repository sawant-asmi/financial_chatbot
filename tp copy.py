from neuralintents import GenericAssistant
import matplotlib.pyplot as plt
# import pandas as pd
# import pandas_datareader as web
import mplfinance as mpf
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
# import sys
# from io import StringIO

import pickle 
import sys
import datetime as dt

st.set_page_config(page_title="ae meri narazgi", layout="wide")
# Add CSS styling to increase font size

st.markdown(
    """
    <style>
    .css-1t42vgz {
        font-size: 300px; /* Adjust the font size as needed */
    
    </style>
    """,
    unsafe_allow_html=True
)

# portfolio = {'AAPL':20, 'TSLA': 5, 'GS': 10}



# skills= st.sidebar.text_input("Enter func")
# date1= st.sidebar.text_input("Enter Date")

with open('portfolio.pkl','rb') as f:
    portfolio = pickle.load(f)


def save_portfolio():
    with open('portfolio.pkl','wb') as f:
        pickle.dump(portfolio,f)
    
def add_portfolio():
    ticker = st.text_input("Enter ticker",key=1)
    amount = st.text_input("Enter number of shares",key=2)

    if ticker in portfolio.keys():
        portfolio[ticker] += int(amount)
    else:
        portfolio[ticker] = int(amount)

    save_portfolio()

def remove_portfolio():
    ticker = st.text_input("Which stock do you want to sell: ",key=3)
    amount = st.text_input("How many shares do you want to sell: ",key=4)

    if ticker in portfolio.keys():
        if int(amount) <= portfolio[ticker]:
            portfolio[ticker] -= int(amount)
            if portfolio[ticker] == 0:
                portfolio.pop(ticker)
            save_portfolio()
        else:
            st.write("You dont have enough shares!:")
    else:
        st.write("You dont own any shares of {ticker}")

def show_portfolio():
    st.write("Your portfolio: ")
    for ticker in portfolio.keys():
        st.write(f"You own {portfolio[ticker]} shares of {ticker}")

def portfolio_worth():
    sum = 0
    for ticker in portfolio.keys():
        data = yf.download(ticker,progress=False)
        # data = web.DataReader(ticker,'stooq')
        price = data['Close'].iloc[-1]
        sum+= price
    st.write(f"Your portfolio is worth {sum} USD")

def portfolio_gains():
    starting_date = st.text_input("Enter a date for comparison (YYYY-MM-DD): ",key=5)

    sum_now = 0
    sum_then = 0

    try:
        for ticker in portfolio.keys():
            # data= web.DataReader(ticker,'stooq')
            data = yf.download(ticker,progress=False)
            price_now = data['Close'].iloc[-1]
            price_then = data.loc[data.index == starting_date]['Close'].values[0]
            sum_now += price_now
            sum_then += price_then

        st.write(f"Relative Gains: {((sum_now-sum_then)/sum_then)*100}%")
        st.write(f"Absolute Gains: {sum_now-sum_then} USD")
    except IndexError:
        st.write("There was no trading on this day")


def plot_chart():
    ticker = st.text_input("Choose a ticker symbol: ",key=1)
    starting_string = st.text_input("Choose a starting date (DD/MM/YYYY): ",key=6)
    plt.style.use('dark_background')

    start = dt.datetime.strptime(starting_string, "%d/%m/%Y")
    end = dt.datetime.now()

    # data = web.DataReader(ticker , 'stooq', start ,end)
    data = yf.download(ticker,start,end,progress=False)

    # colors = mpf.make_marketcolors(up='#00ff00', down="#ff0000", wick = 'inherit', edge='inherit',volume="in")
    # mpf_style=mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=colors)
    # fig, _ = mpf.plot(data, type='candle', style=mpf_style, volume=True, returnfig=True)
    
    # # Convert Matplotlib figure to Plotly figure
    # plotly_fig = tls.mpl_to_plotly(fig)
    
    # # Display the Plotly figure
    # st.plotly_chart(plotly_fig)

    fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'])])

    st.plotly_chart(fig)

# ...
# This code uses Plotly's built-in go.Candlestick to create a candlestick chart directly without relying on the mplfinance library. If the issue persists with this approach, there might be a deeper compatibility problem between libraries in your environment, and further investigation may be needed to identify and resolve the root cause.





def greetings():
    st.write("Hello, I am a Financial Assist bot developed by SIES GST")
   



def bye():
    st.write("Goodbye")
    sys.exit(0)


mappings = {
    'plot_chart': plot_chart,
    'add_portfolio':add_portfolio,
    'remove_portfolio':remove_portfolio,
    'show_portfolio':show_portfolio,
    'portfolio_worth':portfolio_worth,
    'portfolio_gains':portfolio_gains,
    'bye':bye,
    'greetings':greetings

}

assistant = GenericAssistant('intents.json',mappings,"financial_assistant_model")

assistant.train_model()
assistant.save_model()
# assistant.load_model()
message = st.sidebar.text_input("Enter a message:", key="99")
# original_stdout = sys.stdout
# sys.stdout = StringIO()
response=assistant.request(message)
# sys.stdout = original_stdout

if st.sidebar.button("Send"):
     st.write(response)

elif response:
    st.write(response)




