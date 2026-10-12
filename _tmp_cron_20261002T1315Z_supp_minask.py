import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            rows.append((ya + na, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"Markets with both books priced: {len(rows)}")
    print("Top 8 by MIN-ASK sum (true best bracket candidate):")
    for s, q, ya, na, liq in rows[:8]:
        flag = "ARB" if s < 1.0 else ("NEAR" if s <= 1.005 else "")
        print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q} {flag}")
    print(f"True floor: {rows[0][0]:.4f}" if rows else "no data")

asyncio.run(supp())
