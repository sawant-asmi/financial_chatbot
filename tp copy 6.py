from neuralintents import GenericAssistant
import matplotlib.pyplot as plt
import mplfinance as mpf
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from forex_python.converter import CurrencyRates

import pickle 
import sys
import datetime as dt
import requests

st.set_page_config(page_title="Finance Chatbot", layout="wide")
st.markdown(
    """
    <style>
    .css-1t42vgz {
        font-size: 300px; /* Adjust the font size as needed */
    
    </style>
    """,
    unsafe_allow_html=True
)

def convert_usd_to_inr(amount_usd):
    api_key = 'YOUR_API_KEY'
    url = f"https://api.apilayer.com/exchangerates_data/latest?base=USD&symbols=INR&apikey={api_key}"

    try:
        response = requests.get(url)
        data = response.json()
        inr_rate = data['rates']['INR']
        amount_inr = amount_usd * inr_rate
        return amount_inr
    except Exception as e:
        st.write(f"Error fetching exchange rates: {e}")
        return None
    

# portfolio = {'AAPL':20, 'TSLA': 5, 'GS': 10}

with open('portfolio.pkl','rb') as f:
    portfolio = pickle.load(f)


def save_portfolio():
    with open('portfolio.pkl','wb') as f:
        pickle.dump(portfolio,f)
    
def add_portfolio():
    st.write("Please enter the following data:")
    ticker = st.text_input("Enter ticker", key=1)
    amount = st.text_input("Enter number of shares", key=2) 

    if ticker and amount and amount.isdigit():  
        amount = int(amount)
        if ticker in portfolio.keys():
            portfolio[ticker] += amount
        else:
            portfolio[ticker] = amount
        save_portfolio()
    else:
        st.write("Please enter a valid ticker and a numeric amount.")


def remove_portfolio():
    st.write("Please enter the following data:")
    ticker = st.text_input("Which stock do you want to sell: ", key=3)
    amount = st.text_input("How many shares do you want to sell: ", key=4)

    if ticker and ticker in portfolio.keys():
        if amount and amount.isdigit() and int(amount) <= portfolio[ticker]:
            amount = int(amount)
            portfolio[ticker] -= amount
            if portfolio[ticker] == 0:
                portfolio.pop(ticker)
            save_portfolio()
        elif not amount:
            st.write("Please enter the number of shares you want to sell.")
        else:
            st.write("You don't have enough shares!")
    elif not ticker:
        st.write("Please enter the stock you want to sell.")
    else:
        st.write(f"You don't own any shares of {ticker}")


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

    # st.write(f"Your portfolio is worth {sum} USD or approximately {sum_inr:.2f} INR.")
    st.write(f"Your portfolio is worth {sum} USD.")

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
        relative_gains_usd = sum_now - sum_then
        relative_gains_percent = ((sum_now - sum_then) / sum_then) * 100

        

        st.write(f"Relative Gains (USD): {relative_gains_usd} USD")

        st.write(f"Relative Gains (%): {relative_gains_percent}%")
        
    except IndexError:
        st.write("There was no trading on this day")


def plot_chart():
    st.write("Please enter the following data:")
    ticker = st.text_input("Choose a ticker symbol: ", key=1)
    starting_string = st.text_input("Choose a starting date (DD/MM/YYYY): ", key=6)
    
    if starting_string:
        try:
            start = dt.datetime.strptime(starting_string, "%d/%m/%Y")
            end = dt.datetime.now()
            data = yf.download(ticker,start,end,progress=False)
            fig = go.Figure(data=[go.Candlestick(x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'])])
            
            st.write("Here is the requested plot:")
            st.plotly_chart(fig)
        except ValueError:
            st.write("Please enter a valid date in the format DD/MM/YYYY.")
    else:
        st.write("Please enter a starting date.")




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

# assistant.train_model()
# assistant.save_model()
assistant.load_model()
message = st.sidebar.text_input("Enter a message:", key="99")
response=assistant.request(message)

if st.sidebar.button("Send"):
      if response is not None:
        st.write(response)

elif response:
     if response is not None:
        st.write(response)

