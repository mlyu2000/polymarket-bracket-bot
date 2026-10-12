import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    brackets = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        s = yp + np
        if s < 1.0:
            brackets.append((s, yp, np, m.question[:60], m.liquidity))
        rows.append((s, yp, np, m.question[:60], m.liquidity))
    rows.sort()
    brackets.sort()
    return priced, brackets, rows

priced, brackets, rows = asyncio.run(scan())
print(f"priced markets: {priced}")
print(f"TRUE brackets (min-ask sum < 1.00): {len(brackets)}")
for s, yp, np, q, liq in brackets[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("lowest 8 sums (min-ask):")
for s, yp, np, q, liq in rows[:8]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
cnt = sum(1 for r in rows if r[0] <= 1.005)
print(f"near-misses <=1.005 (min-ask): {cnt}")
