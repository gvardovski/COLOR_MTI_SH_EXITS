Long Trading Strategy with Chandelier Exit Stop-Loss

This strategy combines an indicator-based entry with a Chandelier Exit stop-loss and tests optimal exit timing after a stop is triggered.

1. Entry Rules
Signal: You enter a long trade when your indicator turns green (indicating bullish conditions).
Chandelier Exit Calculation at Entry:
At the moment of entering the trade, calculate the Chandelier Exit:
Initial stop-loss is set to this Chandelier Exit value.
This ensures you have a volatility-adjusted protective stop immediately at the trade start.

2. Stop-Loss / Risk Management
The stop-loss does not move after entry; it is fixed at the Chandelier Exit level calculated at entry.
If the price hits the stop-loss, the trade is considered “stopped out,” but the strategy continues evaluating the position for exit timing.

3. Exit Rules / Testing Exit Timing
After the stop-loss is hit, the strategy tests exiting the trade at different time delays:
0 day after stop-loss hit → exit immediately
1 day after stop-loss hit → exit next trading day
2 days after stop-loss hit → exit two trading days later
This allows backtesting to determine the optimal exit delay for maximum profitability or minimum loss.

4. Trade Management Summary
Step	Action
Entry	Indicator turns green → enter long
Stop-Loss	Calculate Chandelier Exit at entry → place stop-loss
Exit	If stop-loss hit → test exits 0, 1, 2 days after SL
Risk Control	Stop-loss is fixed, protects downside
Profit Management	Strategy does not move stop; exit timing optimized post-SL
