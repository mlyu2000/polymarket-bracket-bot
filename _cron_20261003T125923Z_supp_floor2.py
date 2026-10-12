import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    # filter to markets with 2 clob token ids
    markets = [m for m in markets if m.clob_token_ids and len(m.clob_token_ids) >= 2]
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    empty = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            empty += 1
            continue
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        rows.append((yes_min + no_min, m.question[:60], yes_min, no_min, m.liquidity))
    rows.sort()
    return rows, len(markets), empty

for attempt in range(2):
    rows, n, empty = asyncio.run(scan())
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"[attempt {attempt+1}] token-pair markets={n}, priced={len(rows)}, empty-books={empty}")
    if brackets:
        print(f"  BRACKETS: {len(brackets)}")
        for t,q,yp,np_,l in brackets[:10]: print(f"  {t:.4f} | {q}")
    else:
        print("  brackets: 0")
    if rows:
        print(f"  best sums: " + ", ".join(f"{r[0]:.4f} ({r[1][:40]})" for r in rows[:5]))
    if attempt == 0:
        await_async = asyncio.sleep(5)
        asyncio.run(await_async)
