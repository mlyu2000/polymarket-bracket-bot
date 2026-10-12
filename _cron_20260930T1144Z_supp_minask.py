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
    el = time.time() - t0
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ys = sorted(float(a['price']) for a in yes_book.asks)
        ns = sorted(float(a['price']) for a in no_book.asks)
        rows.append((ys[0], ns[0], m.question[:70], m.liquidity))
    rows.sort(key=lambda r: r[0] + r[1])
    print(f"--- MIN-ASK FLOOR SWEEP ({len(markets)} markets, {el:.1f}s) ---")
    print("TRUE brackets (minYes+minNo < 1.000):")
    n = 0
    for y, nn, q, liq in rows:
        s = y + nn
        if s < 1.000:
            n += 1
            print(f"  sum={s:.3f} | Yes@{y:.3f} No@{nn:.3f} | liq={liq} | {q}")
    if n == 0:
        print("  (none)")
    print(f"Lowest 6 combined min-ask sums:")
    for y, nn, q, liq in rows[:6]:
        print(f"  sum={y+nn:.3f} | Yes@{y:.3f} No@{nn:.3f} | liq={liq} | {q}")
    below = sum(1 for r in rows if r[0] + r[1] <= 1.005)
    print(f"Markets with min-ask sum <= 1.005: {below}")

asyncio.run(scan())
