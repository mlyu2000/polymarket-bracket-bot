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

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        rows.append((total, m.question[:60], ya, na, m.liquidity))

    rows.sort()
    print(f"min-ask supplement: {priced}/{len(markets)} priced in {dt:.1f}s")
    print(f"true floor: {rows[0][0]:.4f}" if rows else "no priced markets")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses (min-ask sum <= 1.005): {len(nm)}")
    for total, q, ya, na, liq in nm[:8]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print("top-8 lowest sums overall:")
    for total, q, ya, na, liq in rows[:8]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"brackets (min-ask sum < 1.00): {len(brackets)}")

asyncio.run(scan())
