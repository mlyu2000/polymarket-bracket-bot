# Functional and Non-Functional Requirements

## 1. Functional Requirements

### FR-001: Market Filtering
The system MUST only scan markets that are:
- Active (not closed or resolved).
- Binary (exactly two tokens: Yes and No).

### FR-002: Bracket Calculation
The system MUST accurately calculate the combined cost of the best available asks.
It MUST apply safety buffers for fees and slippage before evaluating edge.
It MUST calculate the maximum executable volume, which is the minimum of the available volume on the Yes ask and the No ask.

The detection formula:

```
gross_edge = 1.00 - Ask(Yes) - Ask(No)
net_edge   = gross_edge - fee_buffer - slippage_buffer
```

Opportunity is valid only if `net_edge >= MIN_PROFIT_MARGIN`.

### FR-003: Dry Run Mode
The system MUST support a `DRY_RUN` flag. When true, the system MUST NOT send any transactions, but MUST log the exact details of the opportunity.

## 2. Non-Functional Requirements

### NFR-001: Speed
The detection loop should run frequently (e.g., polling every 5-10 seconds, or using WebSockets for real-time updates) because bracket opportunities are quickly arbitraged away by other bots.

### NFR-002: Reliability
The bot must handle API rate limits gracefully, using exponential backoff if Polymarket's API returns 429 errors.
