# Implementation Tasks

## Phase 1: Foundation (MVP)

### Task 1.1: Project Setup
- [x] Create project directory structure
- [ ] Initialize Python virtual environment
- [ ] Create `config.py` with environment variables and defaults
- [ ] Create `.env.example` template

### Task 1.2: Polymarket API Client
- [ ] Implement `polymarket_api.py`:
  - [ ] Fetch active binary markets from Gamma API
  - [ ] Fetch order books from CLOB API
  - [ ] Handle rate limiting (429 → exponential backoff)
  - [ ] Parse double-encoded JSON fields

### Task 1.3: Detection Engine
- [ ] Implement `detector.py`:
  - [ ] Calculate combined ask prices (Yes + No)
  - [ ] Calculate maximum executable volume (min of both sides)
  - [ ] Filter by MIN_PROFIT_MARGIN threshold
  - [ ] Filter by MAX_CAPITAL_PER_TRADE constraint

### Task 1.4: Dry-Run Executor
- [ ] Implement `executor.py`:
  - [ ] Dry-run logging mode (console output)
  - [ ] Format opportunity details with exact math
  - [ ] Placeholder for live execution (future)

### Task 1.5: Main Loop
- [ ] Implement `main.py`:
  - [ ] Async event loop with polling interval
  - [ ] Market discovery → order book fetch → detection cycle
  - [ ] Graceful shutdown handling (SIGINT/SIGTERM)
  - [ ] Statistics tracking (opportunities found, avg margin)

### Task 1.6: Tests
- [ ] Implement `tests/test_detector.py`:
  - [ ] Test bracket calculation math
  - [ ] Test volume overlap calculation
  - [ ] Test margin threshold filtering
  - [ ] Test edge cases (zero volume, closed markets)

## Phase 2: Execution (Future)
- [ ] Wallet integration (EIP-712 signatures)
- [ ] Live order placement on CLOB
- [ ] Concurrent order submission (Promise.all pattern)
- [ ] Fill verification
- [ ] Leg-in risk mitigation (fallback cancellations)
