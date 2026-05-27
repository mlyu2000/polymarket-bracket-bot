# Product Specification

## Product Name

Polymarket Bracket Arbitrage Scanner

## Product Goal

Provide a completely automated, low-risk yield generation tool that exploits temporary order book dislocations on Polymarket.

## Target User

A conservative crypto trader who wants to earn yield on USDC without taking directional market risk.

## User Problems

1. Finding bracket opportunities manually is impossible; they exist for seconds or minutes.
2. Calculating the exact overlapping volume available on both sides is tedious.
3. Executing both sides manually risks price slippage.

## User Outcomes

The user should be able to:
- Run the bot in the background.
- See a console log whenever a bracket opportunity is found.
- See the exact math: "Found opportunity: Yes at 0.45, No at 0.52. Total: 0.97. Max Size: 100 shares. Potential Profit: $3.00".
- (When live) Automatically execute the trades and lock in the profit.

## Key Metrics
- Number of opportunities detected per day.
- Average profit margin per opportunity.
- Execution success rate (both legs filled).
