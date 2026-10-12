import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs, batch_size=20)
    cnt = 0
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            y = float(yb.asks[0]['price'])
            n = float(nb.asks[0]['price'])
            s = y+n
            if s <= 1.005:
                cnt += 1
                print(s, m.question[:50])
    print('total', cnt)

asyncio.run(test())
