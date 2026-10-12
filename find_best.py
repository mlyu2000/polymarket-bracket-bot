import asyncio
from polymarket_api import PolymarketAPI
from config import Config

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    min_total = 1.1
    best = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        yes_price = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
        no_price = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
        total = yes_price + no_price
        if total < min_total:
            min_total = total
            best = (m.question, yes_price, no_price, m.liquidity)
    print("best", min_total, best)

asyncio.run(t())
