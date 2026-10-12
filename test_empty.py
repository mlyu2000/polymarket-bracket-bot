import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs, batch_size=20)
    counts = {'both_empty':0, 'yes_empty':0, 'no_empty':0, 'total':0}
    for m, (yes_b, no_b) in zip(markets, books):
        counts['total'] += 1
        if not yes_b or not no_b:
            counts['both_empty'] += 1
            continue
        if not yes_b.asks:
            counts['yes_empty'] += 1
        if not no_b.asks:
            counts['no_empty'] += 1
    print(counts)

asyncio.run(test())
