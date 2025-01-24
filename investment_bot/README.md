```OUTLINE OF TOOL:

investment_bot/ 
│
├── data/
│   ├── historical_data.csv  # Store downloaded historical data, will update when data collection is complete.
│
├── scripts/
│   ├── data_collection.py    # Script for collecting and updating data
│   ├── model_training.py     # Script for training and updating the model
│   ├── prediction.py         # Script for making predictions and executing trades
│   ├── rebalance.py          # Script for rebalancing the portfolio
│   ├── config.py             # Configuration file
|   ├── model.pkl             # Model package 
│
├── logs/
│   ├── bot.log               # Log file to track operations
│
├── main.py                   # Main script to run the entire process
├── requirements.txt          # Dependencies file
└── README.md                 # Project documentation
```
