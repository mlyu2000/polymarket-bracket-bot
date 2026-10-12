import asyncio
from polymarket_api import PolymarketAPI

async def test():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=2000)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    count = 0
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            yes_first = float(yb.asks[0]['price'])
            no_first = float(nb.asks[0]['price'])
            if yes_first + no_first < 1.0:
                count += 1
                print(f"{yes_first+no_first:.4f} | {m.question[:70]}")
    print(f"Found {count} with first ask sum <1.0")

asyncio.run(test())
