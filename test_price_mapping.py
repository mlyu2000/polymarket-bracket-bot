import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    for m in markets:
        print("Question:", m.question[:60])
        print("  outcome_prices:", m.outcome_prices)
        print("  clob_token_ids:", m.clob_token_ids)
        yes_id, no_id = m.clob_token_ids
        book0 = await api.fetch_order_book(yes_id)
        book1 = await api.fetch_order_book(no_id)
        if book0 and book0.asks:
            best_ask0 = min(float(a['price']) for a in book0.asks)
        else:
            best_ask0 = None
        if book1 and book1.asks:
            best_ask1 = min(float(a['price']) for a in book1.asks)
        else:
            best_ask1 = None
        print(f"  best_ask0={best_ask0}, best_ask1={best_ask1}")
        if book0 and book0.bids:
            best_bid0 = max(float(b['price']) for b in book0.bids)
        else:
            best_bid0 = None
        if book1 and book1.bids:
            best_bid1 = max(float(b['price']) for b in book1.bids)
        else:
            best_bid1 = None
        print(f"  best_bid0={best_bid0}, best_bid1={best_bid1}")

asyncio.run(test())
