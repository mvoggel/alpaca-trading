import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
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
    df['RSI'] = compute_rsi(df['Close'])  # Define your own RSI calculation
    df.dropna(inplace=True)
    return df

def train_model():
    logger.info("Starting model training process")
    
    # Load the data
    data = pd.read_csv('data/historical_data.csv')
    
    # Apply feature engineering
    data = feature_engineering(data)
    
    # Check if the data is empty after feature engineering
    if data.empty:
        logger.error("No data available for training after feature engineering. Please check the data collection step.")
        raise ValueError("No data available for training. Please check the data collection step.")
    
    # Prepare features (X) and target (y)
    X = data[['MA50', 'RSI']]
    y = (data['Close'].shift(-1) > data['Close']).astype(int)

    # Check if X or y is empty before proceeding
    if X.empty or y.empty:
        logger.error("Features or target data are empty. Cannot proceed with model training.")
        raise ValueError("No data available for training. Please check the data collection step.")

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Train the model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Save the trained model
    joblib.dump(model, 'scripts/model.pkl')
    logger.info("Model training complete and saved to scripts/model.pkl")


if __name__ == "__main__":
    train_model()
    logger.info("Model training process completed")
