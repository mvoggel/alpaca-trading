#!/usr/bin/env python3.10.11

import subprocess
import sys
import logging

# Ensure the correct path is used
sys.path.insert(0, 'C:\\Users\\matth\\OneDrive\\Desktop\\investment_bot\\env\\lib\\site-packages')

# Configure logging
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_bot():
    try:
        logger.info("Starting data collection")
        print("Starting data collection...")
        subprocess.run(['python', 'scripts/data_collection.py'], check=True)
        logger.info("Data collection completed")
        print("Data collection completed.")

        logger.info("Starting model training")
        print("Starting model training...")
        subprocess.run(['python', 'scripts/model_training.py'], check=True)
        logger.info("Model training completed")
        print("Model training completed.")

        logger.info("Starting prediction")
        print("Starting prediction...")
        subprocess.run(['python', 'scripts/prediction.py'], check=True)
        logger.info("Prediction completed")
        print("Prediction completed.")

        logger.info("Starting rebalancing")
        print("Starting rebalancing...")
        subprocess.run(['python', 'scripts/rebalance.py'], check=True)
        logger.info("Rebalancing completed")
        print("Rebalancing completed.")

    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    logger.info("Investment bot started")
    print("Investment bot started...")
    run_bot()
    logger.info("Investment bot completed its run.")
    print("Investment bot completed its run.")
