import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    candidates = []
    for m, (yes_book, no_book) in zip(markets, books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        total = yes_min + no_min
        if total < 1.005:
            candidates.append((total, m.question[:80], yes_min, no_min, m.liquidity))
    candidates.sort()
    print(f"found {len(candidates)} candidates <1.005")
    for c in candidates[:20]:
        print(f"{c[0]:.4f} | Yes {c[2]:.3f} No {c[3]:.3f} liq {c[4]} | {c[1]}")

asyncio.run(find())
