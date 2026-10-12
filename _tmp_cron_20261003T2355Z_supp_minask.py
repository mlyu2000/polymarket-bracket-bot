import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    near = []
    brackets = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        if total < 1.00:
            brackets.append((total, m.question[:60], yp, np, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:50], yp, np, m.liquidity))
    near.sort()
    brackets.sort()
    return markets, priced, brackets, near, dt

markets, priced, brackets, near, dt = asyncio.run(scan())
print(f"BEST-ASK SCAN: {len(markets)} markets ({priced} priced) in {dt:.1f}s")
print(f"TRUE BRACKETS (sum<1.00): {len(brackets)}")
for t, q, yp, np, liq in brackets[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"Near-misses (<=1.005, best ask): {len(near)}")
for t, q, yp, np, liq in near[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
floor = min([t for t,_,_,_,_ in brackets] + [t for t,_,_,_,_ in near], default=None)
print(f"Floor sum (best-ask): {floor}")
