import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        # Find best ask for yes, best ask for no
        yes_ask = None
        no_ask = None
        if yes_book and yes_book.asks:
            yes_ask = min(float(a['price']) for a in yes_book.asks)
        if no_book and no_book.asks:
            no_ask = min(float(a['price']) for a in no_book.asks)
        # Maybe we need to use bids for no?
        if no_book and no_book.bids:
            no_bid = max(float(b['price']) for b in no_book.bids)
            # Actually to buy NO token, we need ask price
            # But if asks empty, maybe token is inverted?
            # Let's check if we should use yes_book for no and no_book for yes?
            pass
        print(m.question[:50], yes_ask, no_ask)
        if yes_ask and no_ask:
            print("  sum", yes_ask + no_ask)

asyncio.run(test())
