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
    best_totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.yes_price, opp.no_price, opp.max_shares, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask = min(float(a['price']) for a in yes_book.asks)
            no_ask = min(float(a['price']) for a in no_book.asks)
            total = yes_ask + no_ask
            if total <= 1.005:
                best_totals.append((total, yes_ask, no_ask, m.liquidity, m.question[:60]))

    best_totals.sort()
    return len(markets), opps, best_totals, scan_time

markets_n, opps, best_totals, t = asyncio.run(scan())
print(f"Scan: {markets_n} markets in {t:.1f}s (best-ask / min-price method)")
print(f"BRACKETS (min-ask sum < 1.00): {len(opps)}")
for s, e, yp, np_, sh, q in sorted(opps):
    print(f"  sum={s:.4f} edge={e:.4f} Yes@{yp:.3f} No@{np_:.3f} {sh} shares liq-gated | {q}")
print(f"Near-misses (min-ask sum <= 1.005): {len(best_totals)}")
for total, yp, np_, liq, q in best_totals[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
