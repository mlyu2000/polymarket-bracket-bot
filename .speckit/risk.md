# Risk Management & Edge Cases

## 1. Leg-In Risk (Execution Risk)
**Scenario:** The bot sends a buy order for Yes at $0.45 and No at $0.52. The Yes order fills, but the No order fails (e.g., someone else bought the No shares a millisecond faster).
**Result:** The bot is now long "Yes" at $0.45, holding unhedged directional risk.
**Mitigation (Future Live Phase):** The execution engine must immediately attempt to buy the next available "No" shares up to a breakeven price (e.g., up to $0.55). If it cannot, it must immediately sell the "Yes" shares to flatten the position, taking a small loss to prevent a total loss.

## 2. Fee Assessment
Polymarket occasionally changes its fee structure. If a 1% fee is introduced, a bracket of $0.99 is no longer profitable.
**Mitigation:** The `MIN_PROFIT_MARGIN` config variable must always be set high enough to cover network gas fees and any platform taker fees.

## 3. Invalid Markets
Some markets resolve to "Invalid" (e.g., if the event is cancelled). In this case, Polymarket usually refunds the initial capital, but capital is locked until resolution.
**Mitigation:** Limit the maximum capital deployed per market to avoid locking up the entire portfolio in a disputed market.

## 4. API Reliability
**Scenario:** Polymarket API goes down or returns stale data.
**Mitigation:** Implement circuit breaker pattern — pause scanning after N consecutive failures, resume with exponential backoff.

## 5. Market Data Staleness
**Scenario:** Bracket opportunity detected but prices changed before execution.
**Mitigation:** Validate order book freshness timestamp before execution; reject if older than 2 seconds.
