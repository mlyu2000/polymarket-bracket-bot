import asyncio
from polymarket_api import PolymarketAPI
from config import Config

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=3)
    for m in markets:
        print("Market:", m.question[:80])
        print("outcomes:", m.outcomes)
        print("outcome_prices:", m.outcome_prices)
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if yes_book:
            print("yes book last_trade:", yes_book.last_trade_price)
            print("yes asks first 3:", [a['price'] for a in yes_book.asks[:3]])
            print("yes bids first 3:", [a['price'] for a in yes_book.bids[:3]])
        if no_book:
            print("no book last_trade:", no_book.last_trade_price)
            print("no asks first 3:", [a['price'] for a in no_book.asks[:3]])
            print("no bids first 3:", [a['price'] for a in no_book.bids[:3]])
        print("---")
        await asyncio.sleep(0.1)

asyncio.run(f())
