import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    priced = 0
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        if total < 1.0:
            brackets.append((total, m.question[:60], ya, na, m.liquidity))
        rows.append((total, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    return rows, brackets, priced, len(markets), dt

rows, brackets, priced, nmarkets, dt = asyncio.run(scan())
print(f"Supp best-ask pass: {nmarkets} markets, {priced} with both-side asks, {dt:.1f}s")
print(f"TRUE BRACKETS (min asks, sum<1.0): {len(brackets)}")
for total, q, ya, na, liq in sorted(brackets):
    print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
near = [r for r in rows if r[0] <= 1.005]
print(f"TRUE near-misses (sum<=1.005): {len(near)}")
for total, q, ya, na, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print("FLOOR (top 5 cheapest sums overall):")
for total, q, ya, na, liq in rows[:5]:
    print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | {q}")
