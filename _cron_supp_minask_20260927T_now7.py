import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    sums = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        sums.append((total, m.question[:60], yp, np, m.liquidity))
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))

    sums.sort()
    return markets, sums, brackets

result = asyncio.run(scan())
markets, sums, brackets = result
priced = len(sums)
print(f"SUPP min-ask scan: {len(markets)} markets, {priced} priced books")
print(f"SUPP true brackets (detector): {len(brackets)}")
for t, e, s, q, liq in sorted(brackets):
    print(f"  [BRK] sum={t:.4f} edge={e:.4f} shares={s} liq={liq} | {q}")
print("SUPP floor distribution (min-ask sums):")
for thr in [0.99, 0.995, 1.0, 1.001, 1.002, 1.005, 1.01]:
    print(f"  <= {thr:.3f}: {sum(1 for s in sums if s[0] <= thr)}")
print("SUPP top-8 lowest min-ask sums:")
for total, q, yp, np, liq in sums[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
