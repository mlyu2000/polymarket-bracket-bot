# Architecture Specification

## 1. High-Level Architecture

```text
+-------------------+       +-------------------+
| Polymarket API    |       | Polymarket CLOB   |
| (Market Metadata) |       | (Order Books)     |
+--------+----------+       +--------+----------+
         |                           |
         v                           v
+-------------------------------------------------+
|                  DATA INGESTION                 |
|  - Filter for active, binary markets only       |
|  - Maintain L2 order book snapshots             |
+------------------------+------------------------+
                         |
                         v
+-------------------------------------------------+
|                DETECTION ENGINE                 |
|  - Calculate: Ask(Yes) + Ask(No)                |
|  - Check: Total < (1.0 - Margin)                |
|  - Determine: Min(Size(Yes), Size(No))          |
+------------------------+------------------------+
                         |
                         v
+-------------------------------------------------+
|                EXECUTION ROUTER                 |
|  - Dry Run: Log opportunity to console          |
|  - Live: Send concurrent BUY orders             |
+-------------------------------------------------+
```

## 2. Recommended MVP Code Structure

```
bracket-bot/
├── config.py             # Thresholds and settings
├── polymarket_api.py     # Functions to fetch markets and order books
├── detector.py           # Core math logic for finding brackets
├── executor.py           # Dry-run and live order placement
├── main.py               # Main loop
└── tests/
    └── test_detector.py  # Unit tests for bracket math
```
