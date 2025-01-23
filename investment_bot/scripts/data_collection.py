import yfinance as yf
import pandas as pd
import logging
import requests
import urllib3
import certifi
import ssl
import sys
from datetime import datetime

sys.path.insert(0, 'C:\\Users\\matth\\OneDrive\\Desktop\\investment_bot\\env\\lib\\site-packages')

# Disable SSL warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create a custom SSL context using the certifi certificate bundle
ssl_context = ssl.create_default_context(cafile=certifi.where())

def download_data(tickers, start_date, end_date):
    data = pd.DataFrame()  # Initialize an empty DataFrame
    
    for ticker in tickers:
        logger.info(f"Downloading data for {ticker} from {start_date} to {end_date}")
        try:
            # Pass the custom SSL context to yfinance
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL Error for {ticker}: {e}")
            print(f"SSL Error for {ticker}: {e}")
            continue
        
        if df.empty:
            logger.warning(f"No data found for {ticker} in the given date range.")
            print(f"No data found for {ticker} in the given date range.")
            continue  # Skip to the next ticker if no data is found
        
        df['Ticker'] = ticker
        data = pd.concat([data, df])
        logger.info(f"Downloaded {df.shape[0]} rows for {ticker}.")
        print(f"Downloaded {df.shape[0]} rows for {ticker}.")
    
    if data.empty:
        logger.error("No data collected for any tickers. Please check the tickers and date ranges.")
        print("No data collected for any tickers. Please check the tickers and date ranges.")
    else:
        data.to_csv('data/historical_data.csv', index=False)
        logger.info("Data collection complete and saved to data/historical_data.csv")
        print("Data collection complete!")

if __name__ == "__main__":
    tickers = ['AAPL', 'AMZN', 'JNJ', 'VWO', 'BRK.B', 'NEE', 'VNQ']
    
    # Dynamically set the end date to today's date
    end_date = datetime.today().strftime('%Y-%m-%d')
    
    # Set a fixed start date or calculate dynamically if needed
    start_date = '2024-01-01'  # You can adjust this start date as necessary
    
    logger.info("Starting data collection process")
    download_data(tickers, start_date, end_date)
    logger.info("Data collection process completed")
