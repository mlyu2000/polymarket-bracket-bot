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
        # Try both orders
        for idx, token_id in enumerate([yes_id, no_id]):
            book = await api.fetch_order_book(token_id)
            if book:
                asks = [float(a['price']) for a in book.asks] if book.asks else []
                bids = [float(b['price']) for b in book.bids] if book.bids else []
                print(f"  token{idx} asks min {min(asks) if asks else None} max {max(asks) if asks else None}")
                print(f"  token{idx} bids min {min(bids) if bids else None} max {max(bids) if bids else None}")

asyncio.run(test())
