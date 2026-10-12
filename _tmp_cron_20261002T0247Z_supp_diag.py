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

    none_books = sum(1 for y, n in all_books if y is None or n is None)
    empty_asks = sum(1 for y, n in all_books if y is not None and n is not None
                     and (not y.asks or not n.asks))
    usable = sum(1 for y, n in all_books if y is not None and n is not None
                 and y.asks and n.asks)
    print(f"markets={len(markets)} | fetch-failed(None)={none_books} | empty-asks={empty_asks} | usable={usable}")

asyncio.run(scan())
