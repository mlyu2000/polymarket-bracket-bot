import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    brackets_min = []
    near_min = []
    priced = 0
    unpriced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            unpriced += 1
            continue
        priced += 1
        yb = min(float(a['price']) for a in yes_book.asks)
        nb = min(float(a['price']) for a in no_book.asks)
        total = yb + nb
        if total < 1.0:
            brackets_min.append((total, m.question[:60], yb, nb, m.liquidity))
        elif total <= 1.005:
            near_min.append((total, m.question[:50], yb, nb, m.liquidity))

    brackets_min.sort()
    near_min.sort()
    return len(markets), priced, unpriced, brackets_min, near_min

n, priced, unpriced, brackets_min, near_min = asyncio.run(scan())
print(f"Markets: {n} (priced={priced}, unpriced={unpriced})")
print(f"BEST-ASK BRACKETS (min-sum < 1.00): {len(brackets_min)}")
for total, q, yb, nb, liq in brackets_min[:10]:
    print(f"  {total:.4f} | YesB@{yb:.3f} NoB@{nb:.3f} | liq={liq} | {q}")
print(f"BEST-ASK NEAR-MISSES (<=1.005): {len(near_min)}")
for total, q, yb, nb, liq in near_min[:10]:
    print(f"  {total:.4f} | YesB@{yb:.3f} NoB@{nb:.3f} | liq={liq} | {q}")
allsums = [t for t, *_ in brackets_min] + [t for t, *_ in near_min]
if allsums:
    print(f"FLOOR (best-ask): {min(allsums):.4f}")
