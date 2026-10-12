"""Supplemental near-miss scan using CORRECT best-ask (min price).
asks[0] in CLOB /book payload is the WORST ask (asks are DESC-sorted), so the
verbatim cron script's near-miss block always reports 0. detector.py correctly
uses min(). This script reproduces near-misses with min() best asks.
"""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.liquidity, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_ask = min(float(a['price']) for a in yes_book.asks)
            no_ask = min(float(a['price']) for a in no_book.asks)
            total = yes_ask + no_ask
            if total <= 1.005 and m.liquidity >= Config.MIN_LIQUIDITY_USDC and m.liquidity > 0:
                near_misses.append((total, m.question[:50], yes_ask, no_ask, m.liquidity))

    near_misses.sort()
    print(f"🔍 Supplemental (best-ask min): {len(markets)} markets ({priced} with both books) in {scan_time:.1f}s")
    print(f"✅ BRACKETS via detector: {len(opps)}")
    for total, edge, yp, np_, sh, liq, q in sorted(opps):
        print(f"  🔴 sum={total:.3f} edge={edge:.4f} | Yes@{yp:.3f} No@{np_:.3f} | {sh} shares | liq={liq} | {q}")
    print(f"📊 Near-misses (min-ask sum ≤ 1.005, liq OK): {len(near_misses)}")
    for total, q, yp, np_, liq in near_misses[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    # floor
    all_totals = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks and m.liquidity > 0:
            all_totals.append(min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks))
    if all_totals:
        all_totals.sort()
        print(f"📉 Floor across {len(all_totals)} priced+liquid markets: min sum={all_totals[0]:.3f}")

asyncio.run(scan())
