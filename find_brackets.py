import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1000)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    brackets = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yes_min = min(float(a['price']) for a in yb.asks)
            no_min = min(float(a['price']) for a in nb.asks)
            total = yes_min + no_min
            if total < 1.0:
                brackets.append((total, m.question[:70], m.liquidity, yes_min, no_min))
    brackets.sort(key=lambda x: x[0])
    print(f"Found {len(brackets)} brackets with min ask sum <1.0")
    for b in brackets[:20]:
        print(f"{b[0]:.4f} | liq={b[2]:.1f} | yes={b[3]:.4f} no={b[4]:.4f} | {b[1]}")

asyncio.run(test())
