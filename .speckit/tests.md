# Test Plan

## Unit Tests

### test_detector.py
- `test_bracket_calculation_basic`: Verify Ask(Yes) + Ask(No) < 1.00 detection
- `test_bracket_calculation_with_margin`: Verify MIN_PROFIT_MARGIN filtering
- `test_volume_overlap`: Verify min(V_yes, V_no) calculation
- `test_max_capital_constraint`: Verify MAX_CAPITAL_PER_TRADE limit
- `test_edge_case_zero_volume`: Handle markets with no liquidity
- `test_edge_case_closed_market`: Filter out resolved markets
- `test_edge_case_invalid_market`: Handle invalid/cancelled markets

### test_polymarket_api.py
- `test_fetch_active_markets`: Verify Gamma API response parsing
- `test_fetch_order_book`: Verify CLOB API response parsing
- `test_double_encoded_json`: Verify json.loads() on outcomePrices/clobTokenIds
- `test_rate_limit_handling`: Verify exponential backoff on 429

### test_config.py
- `test_default_values`: Verify safety defaults (dry_run, min_margin, max_capital)
- `test_env_override`: Verify .env file overrides

## Integration Tests (Future)
- `test_full_scan_cycle`: End-to-end scan → detect → log cycle
- `test_api_resilience`: Behavior under network failures

## Test Execution
```bash
pytest tests/ -v
```
