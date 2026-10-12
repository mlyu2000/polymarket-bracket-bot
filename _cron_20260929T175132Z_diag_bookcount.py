import asyncio, logging
from collections import Counter
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    stats = Counter()
    for m, (yb, nb) in zip(markets, books):
        if yb is None or nb is None:
            stats['book_missing(fetch_fail_or_none)'] += 1
        elif not yb.asks or not nb.asks:
            side = []
            if not yb.asks: side.append('yes')
            if not nb.asks: side.append('no')
            stats['asks_empty_on_' + '+'.join(side)] += 1
        else:
            stats['both_asks_present'] += 1
    for k, v in stats.most_common():
        print(f"{k}: {v}")

asyncio.run(main())
