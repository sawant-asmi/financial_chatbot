import pandas as pd
import pandas_datareader as web
import yfinance as yf
ticker = 'GS'
data=yf.download(ticker)

print(data)
