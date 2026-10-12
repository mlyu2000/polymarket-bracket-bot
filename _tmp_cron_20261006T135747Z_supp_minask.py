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

    totals = []
    priced = 0
    brackets = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        s = yp + np
        priced += 1
        totals.append(s)
        if s < 1.0:
            brackets.append((s, yp, np, m.question[:60], m.liquidity))
        elif s <= 1.005:
            near.append((s, yp, np, m.question[:60], m.liquidity))

    brackets.sort()
    near.sort()
    print(f"min-ask supp scan: {len(markets)} markets, {priced} priced, {dt:.1f}s")
    if totals:
        print(f"true floor sum = {min(totals):.4f} | median = {sorted(totals)[len(totals)//2]:.4f}")
    print(f"BRACKETS (min-ask sum < 1.00): {len(brackets)}")
    for s, yp, np, q, liq in brackets[:10]:
        print(f"  🔴 {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"Near-misses (<=1.005): {len(near)}")
    for s, yp, np, q, liq in near[:10]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
