Strategy Overview, Backtest Interpretation, and Exit Delay Evaluation
MTI + Chandelier Exit Strategy (Daily Timeframe)
1. Strategy Overview

This strategy combines:
Market Trend Indicator (MTI) for regime classification
Chandelier Exit for volatility- and trend-adaptive exit placement
It operates on daily bars and applies a configurable confirmation delay to exit execution.
The system should be interpreted primarily as an entry + exit overlay framework, not a standalone alpha engine. Core return generation remains market-beta-driven.

1.1 Market Trend Indicator (MTI)
The MTI assigns one of three states based on moving-average relationships and slope direction:

MTI State	Meaning
G – Green	bullish trend regime
Y – Yellow	neutral or transition phase
R – Red	bearish trend / declining structure

The state is determined by:
the relationship between SMA(20) and SMA(50)
price position relative to SMA(20)
slope direction of SMA(20)
The MTI state is recomputed daily and governs both entry eligibility and exit threshold sensitivity.

1.2 Entry Logic
A long entry is opened when:
the MTI transitions into Green, and
no active long position exists
This prevents repetitive re-entry in persistent bullish regimes and ensures each trend is traded once.

1.3 Exit Logic — Chandelier Exit
Exit levels are calculated using an ATR-adjusted Chandelier Exit. ATR multiplier depends on regime:
MTI State	ATR Multiplier
Green	3.0
Yellow	2.0
Red	1.5

Exit confirmation rule:
A position closes only when the price remains below the Chandelier Exit for N consecutive daily closes, where
N ∈ {0, 1, 2}.

This delay is the parameter under evaluation. Larger values reduce noise-driven stopouts at the cost of slower response to regime deterioration.

2. Backtesting Process
2.1 Data
Historical daily OHLCV loaded via Financial Modeling Prep (FMP)
Unified date window (typically 2015–2025)
Data sorted chronologically
No look-ahead or future leakage

2.2 Indicator Computation
The workflow per day:
MTI state classification
state transition detection
Chandelier Exit recalculation
exit confirmation state storage

2.3 Execution Assumptions

Commissions: 0
Slippage: 0
Position sizing: fixed 1 amount per trade
Initial capital: 10,000 USD

No concurrent overlapping trades
All parameters configurable through an external config

3. Backtest Horizons and Interpretation
Two horizons are considered:

3.1 Full 10-Year Horizon (2015–2025)
Cross-asset observations
Strategy returns consistently below buy-and-hold
Sharpe ratios cluster in 0.3–0.9
Calmar ratios < 0.5
Deep and prolonged drawdowns (25–45%, 1.5–3 years)
No persistent alpha across cycles
Interpretation

Performance is driven primarily by:
market beta exposure
convexity concentrated in rare, strong trends
Reward does not sufficiently compensate tail risk or drawdown duration. Strategy performs better than naive stop-loss but worse than benchmark holding.

3.2 Short 2-Year Horizon (2024–2025)
Observed performance characteristics
Sharpe ratios: 1.5–2.2
Calmar ratios: 2.5–6.7
MaxDD: 11–26%
Returns comparable to benchmark in multiple cases
Interpretation

These strong metrics are regime-dependent:
persistent AI-driven uptrend conditions
few dominant trades inflation Sharpe/Calmar denominators
results lack statistical robustness due to small trade counts

4. Structural Effects of Exit Delay (N Days Under Exit)
General mechanics

Increasing exit delay tends to:
decrease number of trades
increase average holding duration
increase beta exposure
amplify drawdown magnitude and recovery times

Risk-adjusted performance does not improve monotonically; delay is asset-dependent.

Horizon-dependent effects
Horizon	Observed pattern
2015–2025 full cycle	1–2 day delays provide most robustness; 3-day delay increases tail risk
2024–2025 trend-dominated	all variants appear strong; differences statistically unstable
5. Key Takeaways
The strategy is:

✔ regime-adjusted exit framework
✔ volatility-aware trailing stop
✔ useful overlay for trend participation

The strategy is not:

✘ reliable standalone alpha generator
✘ robust across business cycles
✘ stable under parameter perturbations

Recommended interpretation

evaluate performance conditional on regime
avoid extrapolating short-term outperformance
assign allocation according to market trend fragility
apply exit delay selectively and per-asset


NASDAQ: AVGO
+------------+----------------+-----------+--------+----------------------+
| Exit Delay | Total Return % | Max DD %  | Sharpe | Benchmark Return %   |
+------------+----------------+-----------+--------+----------------------+
|     0      |     3.0721     |  1.0137   | 0.7060 |       2010.16        |
|     1      |     3.0708     |  1.0137   | 0.7057 |       2010.16        |
|     2      |     3.0741     |  1.0136   | 0.7064 |       2010.16        |
+------------+----------------+-----------+--------+----------------------+

NASDAQ: GOOG
+------------+----------------+-----------+--------+----------------------+
| Exit Delay | Total Return % | Max DD %  | Sharpe | Benchmark Return %   |
+------------+----------------+-----------+--------+----------------------+
|     0      |     6.7461     |  2.0046   | 0.8610 |       455.695        |
|     1      |     5.4850     |  1.6790   | 0.8643 |       455.695        |
|     2      |     6.4270     |  1.7303   | 0.9268 |       455.695        |
+------------+----------------+-----------+--------+----------------------+

NYSE: AXP
+------------+----------------+-----------+--------+----------------------+
| Exit Delay | Total Return % | Max DD %  | Sharpe | Benchmark Return %   |
+------------+----------------+-----------+--------+----------------------+
|     0      |     3.0227     |  0.9215   | 0.7676 |       511.74         |
|     1      |     3.0233     |  0.9215   | 0.7678 |       511.74         |
|     2      |     3.1421     |  0.9205   | 0.7975 |       511.74         |
+------------+----------------+-----------+--------+----------------------+

NYSE: LLY
+------------+----------------+-----------+---------+----------------------+
| Exit Delay | Total Return % | Max DD %  | Sharpe  | Benchmark Return %   |
+------------+----------------+-----------+---------+----------------------+
|     0      |     9.5574     |  3.0750   | 0.8512  |      1346.73         |
|     1      |     9.6095     |  3.0735   | 0.8560  |      1346.73         |
|     2      |     9.6041     |  3.0736   | 0.8555  |      1346.73         |
+------------+----------------+-----------+---------+----------------------+

NYSE: GS
+------------+----------------+-----------+--------+----------------------+
| Exit Delay | Total Return % | Max DD %  | Sharpe | Benchmark Return %   |
+------------+----------------+-----------+--------+----------------------+
|     0      |     6.7461     |  2.0046   | 0.8610 |       455.69         |
|     1      |     5.4850     |  1.6790   | 0.8643 |       455.69         |
|     2      |     6.4270     |  1.7303   | 0.9268 |       455.69         |
+------------+----------------+-----------+--------+----------------------+
