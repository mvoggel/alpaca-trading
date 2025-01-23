import alpaca_trade_api as tradeapi
from config import API_KEY, API_SECRET, BASE_URL
import logging
import time
import sys

# Set path to libraries (if needed)
sys.path.insert(0, 'C:\\Users\\matth\\OneDrive\\Desktop\\investment_bot\\env\\lib\\site-packages')

# Configure logging
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)  # Create a logger object for the current module

MIN_ORDER_VALUE = 1.00  # Minimum order value required by Alpaca
MIN_DIFF = 0.01  # Minimum percentage difference for rebalancing to trigger
DELAY_PERIOD = 30 * 24 * 60 * 60  # 30 days in seconds (delay for wash trades)

# Dictionary to store the last time a stock was sold
recently_sold = {}

def rebalance_portfolio(target_allocations):
    api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')
    account = api.get_account()
    equity = float(account.equity)
    
    positions = api.list_positions()
    total_value = sum([float(position.market_value) for position in positions])
    
    current_time = time.time()  # Get current time in seconds

    for symbol, target_pct in target_allocations.items():
        target_value = target_pct * equity
        current_value = next((float(pos.market_value) for pos in positions if pos.symbol == symbol), 0)
        price = api.get_latest_trade(symbol).price
        
        # Check for recently sold stocks to prevent wash trades
        if symbol in recently_sold and current_time - recently_sold[symbol] < DELAY_PERIOD:
            logger.info(f"Skipping {symbol} due to wash trade prevention. Last sold {int((current_time - recently_sold[symbol]) / (24 * 60 * 60))} days ago.")
            continue  # Skip rebalancing for this stock to avoid wash trade

        # Selling logic
        if current_value > target_value:
            qty_to_sell = (current_value - target_value) / price
            qty_to_sell = round(qty_to_sell, 3)
            order_value = qty_to_sell * price
            
            if order_value >= MIN_ORDER_VALUE and abs((current_value - target_value) / current_value) >= MIN_DIFF:
                try:
                    api.submit_order(
                        symbol=symbol,
                        qty=qty_to_sell,
                        side='sell',
                        type='market',
                        time_in_force='day'
                    )
                    logger.info(f"Rebalanced by selling {qty_to_sell} shares of {symbol}")
                    recently_sold[symbol] = current_time  # Record the sale timestamp to prevent wash trades
                except tradeapi.rest.APIError as e:
                    logger.error(f"Failed to sell {symbol}: {e}")
                    print(f"Order for {symbol} skipped due to error: {e}")
            else:
                logger.info(f"Skipped selling {symbol} as the order value ({order_value}) is below the minimum threshold or change is too small.")

        # Buying logic with wash trade prevention
        elif current_value < target_value and symbol not in recently_sold:
            qty_to_buy = (target_value - current_value) / price
            qty_to_buy = round(qty_to_buy, 3)
            order_value = qty_to_buy * price
            
            if order_value >= MIN_ORDER_VALUE and abs((target_value - current_value) / target_value) >= MIN_DIFF:
                try:
                    if qty_to_buy < 1:
                        # Simple fractional order
                        api.submit_order(
                            symbol=symbol,
                            qty=qty_to_buy,
                            side='buy',
                            type='market',
                            time_in_force='day'
                        )
                        logger.info(f"Bought fractional shares: {qty_to_buy} of {symbol}")
                    else:
                        # Full share order with a bracket (complex order)
                        profit_price = round(price * 1.05, 2)
                        stop_price = round(price * 0.95, 2)
                        stop_limit_price = round(stop_price * 0.99, 2)

                        api.submit_order(
                            symbol=symbol,
                            qty=qty_to_buy,
                            side='buy',
                            type='market',
                            time_in_force='gtc',
                            order_class='bracket',
                            take_profit=dict(limit_price=profit_price),
                            stop_loss=dict(stop_price=stop_price, limit_price=stop_limit_price)
                        )
                        logger.info(f"Rebalanced by buying {qty_to_buy} full shares of {symbol}")
                except tradeapi.rest.APIError as e:
                    if "wash trade" in str(e).lower():
                        logger.warning(f"Wash trade detected for {symbol}. Skipping...")
                        recently_sold[symbol] = current_time  # Mark as recently sold to prevent further errors
                    else:
                        logger.error(f"Order for {symbol} failed due to: {e}")
            else:
                logger.info(f"Skipped buying {symbol} as the order value ({order_value}) is below the minimum threshold or change is too small.")
        else:
            if symbol in recently_sold:
                logger.info(f"Skipped buying {symbol} due to wash trade prevention.")

if __name__ == "__main__":
    target_allocations = {
        'AAPL': 0.30,  # Apple
        'AMZN': 0.20,  # Amazon
        'JNJ': 0.15,  # Johnson & Johnson
        'VWO': 0.10,  # Vanguard FTSE Emerging Markets ETF
        'BRK.B': 0.10,  # Berkshire Hathaway Class B
        'NEE': 0.10,  # Nextra Energy, Inc.
        'VNQ': 0.05,  # Vanguard Real Estate ETF
    }
    rebalance_portfolio(target_allocations)
    print("Portfolio rebalancing process completed")
    logger.info("Portfolio rebalancing process completed")
