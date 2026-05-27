# SPEC: Polymarket Bracket Strategy System

## 1. Initiative Name

Polymarket Bracket Arbitrage Bot

## 2. Objective

To passively scan Polymarket binary order books for pricing inefficiencies where `Ask(Yes) + Ask(No) < 1.00` and execute simultaneous buy orders to capture risk-free yield.

## 3. Core Strategy & Math

For any binary market, the payout is exactly $1.00 to the winning token and $0.00 to the losing token.
If a user holds 1 "Yes" token and 1 "No" token, the guaranteed payout at resolution is $1.00.

The bot scans the L2 order book for the lowest Ask prices:
$$P_{\text{yes}} = \text{Best Ask for Yes}$$
$$P_{\text{no}} = \text{Best Ask for No}$$

The bot checks the available volume at those prices:
$$V_{\text{yes}} = \text{Available size at } P_{\text{yes}}$$
$$V_{\text{no}} = \text{Available size at } P_{\text{no}}$$

The maximum executable size $S$ is:
$$S = \min(V_{\text{yes}}, V_{\text{no}}, \text{Max Order Size})$$

The opportunity is valid if:
$$P_{\text{yes}} + P_{\text{no}} + \text{fee\_buffer} + \text{slippage\_buffer} \le 1.00 - \text{Min Margin Threshold}$$

Equivalently:
$$\text{net\_edge} = 1.00 - P_{\text{yes}} - P_{\text{no}} - \text{fee\_buffer} - \text{slippage\_buffer}$$
$$\text{If } \text{net\_edge} \ge \text{Min Margin Threshold}: \text{Execute Buy on Both}$$

## 4. Initial MVP Scope

The MVP must include:
- A REST/WebSocket client to fetch active markets and order books.
- A calculation engine to detect bracket opportunities.
- A logging system to record found opportunities (Paper Trading).
- Unit tests for the calculation logic.

The MVP must NOT include:
- Live execution (wallet keys).
- Multi-leg routing algorithms (yet).

## 5. Architecture Layers

### 5.1 Scanner Layer
- Fetches active binary markets from Polymarket API.
- Subscribes to order book updates for target markets.

### 5.2 Detection Engine
- Calculates combined ask prices.
- Calculates available overlapping volume.
- Filters out markets with low liquidity or imminent resolution.

### 5.3 Execution Layer (Future)
- Constructs two simultaneous `BUY` transactions.
- Uses `Promise.all` or async gathering to submit both orders to the CLOB concurrently.
- Verifies fills.

## 6. Required Safety Defaults

- `EXECUTION_MODE=dry_run` (Default)
- `MIN_PROFIT_MARGIN=0.01` (Require at least 1 cent net edge per pair)
- `FEE_BUFFER=0.005` (0.5 cent buffer for Polymarket taker fees)
- `SLIPPAGE_BUFFER=0.005` (0.5 cent buffer for stale data / latency)
- `MAX_CAPITAL_PER_TRADE=50` (Maximum USDC to deploy per opportunity)
