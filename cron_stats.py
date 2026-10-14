import asyncio, logging, statistics, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    totals = []
    two_sided = 0
    one_sided = 0
    no_book = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb:
            no_book += 1
            continue
        y_ok = bool(yb.asks) and bool(yb.bids)
        n_ok = bool(nb.asks) and bool(nb.bids)
        if y_ok and n_ok:
            two_sided += 1
        else:
            one_sided += 1
            continue
        y = min(float(a['price']) for a in yb.asks)
        n = min(float(a['price']) for a in nb.asks)
        totals.append((y + n, m.question))

    totals.sort()
    n = len(totets := totals)
    def cnt(t):
        return sum(1 for x, _ in totals if x <= t)
    print(f"total markets scanned: {len(markets)}")
    print(f"two-sided: {two_sided} | one-sided: {one_sided} | no book: {no_book}")
    print(f"two-sided pct: {100.0*two_sided/len(markets):.1f}%  (not bracketable: {100.0*(one_sided+no_book)/len(markets):.1f}%)")
    print(f"floor: {totals[0][0]:.4f} | {totals[0][1][:60]}")
    print(f"median: {statistics.median([x for x, _ in totals]):.4f}")
    for band in (1.005, 1.010, 1.020, 1.030):
        print(f"bands <= {band:.3f}: n={cnt(band)}")
    # previously tracked market check
    for q, (x) in [(t[1], t[0]) for t in totals]:
        if 'unemployment' in q.lower():
            print(f"UNEMPLOYMENT MKT IN WINDOW: {x:.4f} | {q[:70]}")

asyncio.run(scan())
