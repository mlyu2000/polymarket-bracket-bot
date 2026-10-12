import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        print("Market:", m.question[:60])
        yes_id, no_id = m.clob_token_ids
        # Try both orders: maybe yes_id actually maps to NO token?
        for token_id, label in [(yes_id, 'yes_id'), (no_id, 'no_id')]:
            book = await api.fetch_order_book(token_id)
            if book:
                asks = book.asks
                bids = book.bids
                print(f"  {label} asks:{len(asks)} bids:{len(bids)}")
                if asks:
                    print(f"    best ask {asks[0]}")
                if bids:
                    print(f"    best bid {bids[0]}")

asyncio.run(test())
