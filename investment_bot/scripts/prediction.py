import pandas as pd
import joblib
import alpaca_trade_api as tradeapi
from config import API_KEY, API_SECRET, BASE_URL
import logging
import sys
sys.path.insert(0, 'C:\\Users\\matth\\OneDrive\\Desktop\\investment_bot\\env\\lib\\site-packages')

# Configure logging
logging.basicConfig(
    filename='logs/bot.log',  # Log file path
    level=logging.INFO,  # Logging level (INFO, DEBUG, ERROR, etc.)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log format
)

logger = logging.getLogger(__name__)  # Create a logger object for the current module

def compute_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def feature_engineering(df):
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['RSI'] = compute_rsi(df['Close'])
    df.dropna(inplace=True)  # Drop any rows with missing values
    return df

def make_prediction():
    logger.info("Starting prediction process")
    model = joblib.load('scripts/model.pkl')
    api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

    data = pd.read_csv('data/historical_data.csv')
    data = feature_engineering(data)
    
    symbols = data['Ticker'].unique()  # Get a list of unique symbols in the data

    for symbol in symbols:
        symbol_data = data[data['Ticker'] == symbol]  # Filter data for the current symbol
        
        if symbol_data.empty:
            logger.warning(f"No data found for {symbol}, skipping prediction.")
            continue
        
        X_latest = symbol_data[['MA50', 'RSI']].iloc[-1:]  # Get the latest features for prediction
        prediction = model.predict(X_latest)

        if prediction[0] == 1:
            amount_to_invest = 25  # Example allocation
            price = api.get_latest_trade(symbol).price
            qty = amount_to_invest / price  # Allow fractional shares
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='day'
            )
            logger.info(f"Bought {symbol} for ${amount_to_invest} at price {price}")
            print(f"Bought {symbol} for ${amount_to_invest} at price {price}")
        else:
            logger.info(f"No action taken for {symbol} based on prediction")
            print(f"No action taken for {symbol} based on prediction")

if __name__ == "__main__":
    make_prediction()
    logger.info("Prediction process completed")
    print("Prediction process completed")
