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
    elapsed = time.time() - t0

    rows = []
    priced = 0
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        total = yes_min + no_min
        priced += 1
        if total < 1.0:
            brackets.append((total, m.question[:60], yes_min, no_min, m.liquidity))
        rows.append((total, m.question[:50], yes_min, no_min, m.liquidity))

    rows.sort()
    near = [r for r in rows if r[0] <= 1.005]
    print(f"TRUE-MIN-ASK pass ({elapsed:.1f}s): {priced}/{len(markets)} markets priced")
    print(f"BRACKETS (min-ask sum < 1.00): {len(brackets)}")
    for total, q, yp, np_, liq in sorted(brackets):
        print(f"  🔴 {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"Near-misses (min-ask sum <= 1.005): {len(near)}")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print("Best 5 overall sums:")
    for total, q, yp, np_, liq in rows[:5]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")

asyncio.run(scan())
