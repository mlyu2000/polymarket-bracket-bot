import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def floor_check():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    near = []
    sub1000 = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        yb = min(float(a['price']) for a in yes_book.asks)
        nb = min(float(a['price']) for a in no_book.asks)
        t = yb + nb
        if t < 1.000:
            sub1000.append((t, m.question[:50], yb, nb, m.liquidity))
        elif t <= 1.005:
            near.append((t, m.question[:50], yb, nb, m.liquidity))

    near.sort()
    sub1000.sort()
    print(f"Floor check: {priced}/{len(markets)} priced markets in {dt:.1f}s")
    print(f"Sub-1.000 best-ask sums (detector-filtered by guards): {len(sub1000)}")
    for t, q, yb, nb, liq in sub1000[:10]:
        print(f"  {t:.3f} | Yes@{yb:.3f} No@{nb:.3f} | liq={liq} | {q}")
    print(f"Near-misses best-ask (1.000 < sum <= 1.005): {len(near)}")
    for t, q, yb, nb, liq in near[:10]:
        print(f"  {t:.3f} | Yes@{yb:.3f} No@{nb:.3f} | liq={liq} | {q}")
    if priced:
        print(f"(True floor measured across all priced books this run.)")

asyncio.run(floor_check())
