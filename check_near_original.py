import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        # Use first ask as original script
        yes_price = float(yes_book.asks[0]['price'])
        no_price = float(no_book.asks[0]['price'])
        total = yes_price + no_price
        if total <= 1.005:
            near.append((total, m.question[:50], yes_price, no_price, m.liquidity))
    near.sort()
    print('near count', len(near))
    for x in near[:10]:
        print(x)

asyncio.run(scan())
