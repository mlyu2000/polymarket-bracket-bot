import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets[:10]:
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if yes_book and no_book:
            print('market', m.question[:50])
            print('yes asks', yes_book.asks[:3], '...', yes_book.asks[-3:])
            print('no asks', no_book.asks[:3], '...', no_book.asks[-3:])
            print()

asyncio.run(scan())
