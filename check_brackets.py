import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check_min():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            print(f"liq={m.liquidity} < min, skip: {m.question[:60]}")
            continue
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_price = min(float(a['price']) for a in yes_book.asks)
        no_price = min(float(a['price']) for a in no_book.asks)
        total = yes_price + no_price
        if total < 1.0:
            print(f"BRACKET! sum={total:.3f} Yes@{yes_price:.3f} No@{no_price:.3f} liq={m.liquidity} | {m.question[:80]}")

asyncio.run(check_min())
