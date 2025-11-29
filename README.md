## Pair Trading Bot

This trading bot has been created respecting PAIR TRADING strategy principles.

My way of coding this bot may not be regular since this is my first time doing anything like this and I designed the strategy myself, I only heard about pair trading during the development.

I find a project like this really interesting since the code I am bulding is applied and connected to the real world.


To run my code automatically I just use the following simple crontab to launch the code every 5 min :

30-59/5 14 * * 1-5 /usr/bin/bash -c 'cd /root/ml_env && source venv/bin/activate && python scripts/trading_bot_project/bot.py >> scripts/trading_bot_project/bot.log 2>&1'

*/5 15-20 * * 1-5 /usr/bin/bash -c 'cd /root/ml_env && source venv/bin/activate && python scripts/trading_bot_project/bot.py >> scripts/trading_bot_project/bot.log 2>&1'


