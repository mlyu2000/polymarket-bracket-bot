import asyncio
from polymarket_api import PolymarketAPI
from config import Config

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    print("Question:", m.question)
    print("Clob token ids:", m.clob_token_ids)
    # Fetch both books
    token_yes = m.clob_token_ids[0]
    token_no = m.clob_token_ids[1]
    yes_book = await api.fetch_order_book(token_yes)
    no_book = await api.fetch_order_book(token_no)
    print("yes_book market:", yes_book.market)
    print("no_book market:", no_book.market)
    # Find min ask
    def min_ask(book):
        if not book or not book.asks:
            return None
        return min(float(a['price']) for a in book.asks)
    print("min yes ask:", min_ask(yes_book))
    print("min no ask:", min_ask(no_book))

asyncio.run(check())
