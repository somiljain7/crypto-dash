# pip install pandas numpy matplotlib streamlit pystan fbprophet cryptocmd plotly
import warnings
warnings.filterwarnings('ignore')  # Hide warnings
import pandas as pd
from IPython import embed
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import seaborn as sns
!pip install pandas_datareader
from pandas_datareader import data as pdr
import yfinance as yf
import matplotlib.dates as mdates
import plotly.express as px
import streamlit as st
import numpy as np
import matplotlib as plt
from datetime import date, datetime
from cryptocmd import CmcScraper
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
from plotly import graph_objs as go
import plotly.io as pio
from pytrends.request import TrendReq
import matplotlib.pyplot as plt

# st.markdown("This application enables you to predict on the future value of any cryptocurrency (available on Coinmarketcap.com), for \
# 	any number of days into the future! The application is built with Streamlit (the front-end) and the Facebook Prophet model, \
# 	which is an advanced open-source forecasting model built by Facebook, running under the hood. You can select to train the model \
# 	on either all available data or a pre-set date range. Finally, you can plot the prediction results on both a normal and log scale.")


def crypto_compare():
    end = datetime.today()
    start = datetime(end.year-1,end.month,end.day)
    yf.pdr_override()
    btc = pdr.get_data_yahoo("BTC-USD", start, end)
    btc.reset_index(inplace=True)
    crypto= btc[['Date','Adj Close']]
    crypto= crypto.rename(columns = {'Adj Close':'BTC'})
    eth = pdr.get_data_yahoo("ETH-USD", start, end)
    eth.reset_index(inplace=True)
    crypto["ETH"]= eth["Adj Close"]
    doge = pdr.get_data_yahoo("DOGE-USD", start, end)
    doge.reset_index(inplace=True)
    crypto["DOGE"]= doge["Adj Close"]
    bnb = pdr.get_data_yahoo("BNB-USD", start, end)
    bnb.reset_index(inplace=True)
    crypto["BNB"]= bnb["Adj Close"]
    # ada = pdr.get_data_yahoo("ADA-USD", start, end)
    # ada = web.DataReader("ADA-USD", 'yahoo', start, end)
    # ada.reset_index(inplace=True)
    # crypto["ADA"]= ada["Adj Close"]
    xrp = pdr.get_data_yahoo("XRP-USD", start, end)
    xrp.reset_index(inplace=True)
    crypto["XRP"]= xrp["Adj Close"]
    dash = pdr.get_data_yahoo("DASH-USD", start, end)
    dash.reset_index(inplace=True)
    crypto["DASH"]= dash["Adj Close"]
    crypto.set_index("Date", inplace=True)
    return crypto
def Homepage():
	compare=crypto_compare()
	st.subheader('Crypto comparative data')
	st.write(compare.head())
	df=compare.reset_index()
	monday_df=df.loc[df['Date'].dt.weekday == 1]
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=monday_df['Date'], y=monday_df['BTC'], name="BTC"))
	fig3 = go.Figure()
	fig3.add_trace(go.Scatter(x=monday_df['Date'], y=monday_df['DOGE'], name="DOGE"))
	fig2 = go.Figure()
	fig2.add_trace(go.Scatter(x=monday_df['Date'], y=monday_df['BNB'], name="BNB"))
	fig4 = go.Figure()
	fig4.add_trace(go.Scatter(x=monday_df['Date'], y=monday_df['XRP'], name="XRP"))
	fig5 = go.Figure()
	fig5.add_trace(go.Scatter(x=monday_df['Date'], y=monday_df['DASH'], name="DASH"))	
	fig.layout.update(title_text='BTC', xaxis_rangeslider_visible=True)
	fig2.layout.update(title_text='ETH', xaxis_rangeslider_visible=True)
	fig3.layout.update(title_text='DOGE', xaxis_rangeslider_visible=True)
	fig4.layout.update(title_text='XRP', xaxis_rangeslider_visible=True)
	fig5.layout.update(title_text='DASH', xaxis_rangeslider_visible=True)
	st.plotly_chart(fig)
	st.plotly_chart(fig2)
	st.plotly_chart(fig3)
	st.plotly_chart(fig4)
	st.plotly_chart(fig5)			
	#embed()

def Forecast():
### Change sidebar color
	st.markdown(
		"""
	<style>
	.sidebar .sidebar-content {
		background-image: linear-gradient(#D6EAF8,#D6EAF8);
		color: black;
	}
	</style>
	""",
		unsafe_allow_html=True,
	)

	### Set bigger font style
	st.markdown(
		"""
	<style>
	.big-font {
		fontWeight: bold;
		font-size:22px !important;
	}
	</style>
	""", unsafe_allow_html=True)

	st.sidebar.markdown("<p class='big-font'><font color='Blue'>Forecaster</font></p>", unsafe_allow_html=True)

	### Select ticker & number of days to predict on
	selected_ticker = st.sidebar.text_input("Select a ticker for prediction (i.e. BTC, ETH, LINK, etc.)", "BTC")
	period = int(st.sidebar.number_input('Number of days to predict:', min_value=0, max_value=1000000, value=365, step=1))
	training_size = int(st.sidebar.number_input('Training set (%) size:', min_value=10, max_value=100, value=100, step=5)) / 100

	### Initialise scraper without time interval
	@st.cache
	def load_data(selected_ticker):
		init_scraper = CmcScraper(selected_ticker)
		df = init_scraper.get_dataframe()
		min_date = pd.to_datetime(min(df['Date']))
		max_date = pd.to_datetime(max(df['Date']))
		return min_date, max_date

	data_load_state = st.sidebar.text('Loading data...')
	min_date, max_date = load_data(selected_ticker)
	data_load_state.text('Loading data... done!')


	### Select date range
	date_range = st.sidebar.selectbox("Select the timeframe to train the model on:", options=["All available data", "Specific date range"])

	if date_range == "All available data":

		### Initialise scraper without time interval
		scraper = CmcScraper(selected_ticker)

	elif date_range == "Specific date range":

		### Initialise scraper with time interval
		start_date = st.sidebar.date_input('Select start date:', min_value=min_date, max_value=max_date, value=min_date)
		end_date = st.sidebar.date_input('Select end date:', min_value=min_date, max_value=max_date, value=max_date)
		scraper = CmcScraper(selected_ticker, str(start_date.strftime("%d-%m-%Y")), str(end_date.strftime("%d-%m-%Y")))

	### Pandas dataFrame for the same data
	data = scraper.get_dataframe()


	def google_trends_analytics(val):
		pytrends = TrendReq(hl='en-US', tz=360) 
		kw_list = [val] # list of keywords to get data 
		pytrends.build_payload(kw_list, cat=0, timeframe='today 12-m') 
		data = pytrends.interest_over_time() 
		data = data.reset_index() 
		fig = px.line(data, x="date", y=kw_list, title='Keyword Web Search Interest Over Time')
		return fig
	fg=google_trends_analytics(selected_ticker)
	st.subheader('Google trends analytics')
	st.plotly_chart(fg)	
	st.subheader('Raw data')
	st.write(data.head())

	### Plot functions
	def plot_raw_data():
		fig = go.Figure()
		fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Close"))
		fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
		st.plotly_chart(fig)

	def plot_raw_data_log():
		fig = go.Figure()
		fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Close"))
		fig.update_yaxes(type="log")
		fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
		st.plotly_chart(fig)
		
	### Plot (log) data
	plot_log = st.checkbox("Plot log scale")
	if plot_log:
		plot_raw_data_log()
	else:
		plot_raw_data()

	### Predict forecast with Prophet
	if st.button("Predict"):

		df_train = data[['Date','Close']]
		df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

		### Create Prophet model
		m = Prophet(
			changepoint_range=training_size, # 0.8
			yearly_seasonality='auto',
			weekly_seasonality='auto',
			daily_seasonality=False,
			seasonality_mode='multiplicative', # multiplicative/additive
			changepoint_prior_scale=0.05
			)

		### Add (additive) regressor
		for col in df_train.columns:
			if col not in ["ds", "y"]:
				m.add_regressor(col, mode="additive")
		
		m.fit(df_train)

		### Predict using the model
		future = m.make_future_dataframe(periods=period)
		forecast = m.predict(future)
		### Show and plot forecast
		st.subheader('Forecast data')
		st.write(forecast.head())
			
		st.subheader(f'Forecast plot for {period} days')
		fig1 = plot_plotly(m, forecast)
		if plot_log:
			fig1.update_yaxes(type="log")
		st.plotly_chart(fig1)

		st.subheader("Forecast components")
		fig2 = m.plot_components(forecast)
		st.write(fig2)

def main():
	with st.sidebar:
		st.subheader("Crypt-Dash: A dashboard for analysis of prices of trending cryptocurrencies and comparision of prices ")
	page = st.sidebar.selectbox(
        "Select a Page",
        [
            "CryptoCompare","Forecast"
        ]
    )
	if page == "CryptoCompare":
		Homepage()
	elif page == "Forecast":
		Forecast()
if __name__ == "__main__":
    main()
