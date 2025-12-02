## Pair Trading Bot

To run my code automatically I just use the following simple crontab to launch the code every 5 min :
```bash
30-59/5 14 * * 1-5 /usr/bin/bash -c 'cd /root/ml_env && source venv/bin/activate && python scripts/trading_bot_project/bot.py >> scripts/trading_bot_project/bot.log 2>&1'

*/5 15-20 * * 1-5 /usr/bin/bash -c 'cd /root/ml_env && source venv/bin/activate && python scripts/trading_bot_project/bot.py >> scripts/trading_bot_project/bot.log 2>&1'
```

My strategy for this project was first, to find some of the most correlated stocks in S&P500 and compute a the average spread between them.
Then every 5 minutes, I check if the spread gets too large or too low I predict that I will adapt back to its normal spread and I thus launch orders accordingly to my prediction. When the spread gets back to normal I close the position for both stocks.
