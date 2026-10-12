import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        print("Question:", m.question[:60])
        print("  outcomes:", m.outcomes)
        print("  outcome_prices:", m.outcome_prices)
        yes_id, no_id = m.clob_token_ids
        book_yes = await api.fetch_order_book(yes_id)
        book_no = await api.fetch_order_book(no_id)
        # For each book, find best ask and best bid
        def summarize(book, name):
            if not book:
                return f"{name}: None"
            asks = [float(a['price']) for a in book.asks] if book.asks else []
            bids = [float(b['price']) for b in book.bids] if book.bids else []
            best_ask = min(asks) if asks else None
            best_bid = max(bids) if bids else None
            return f"{name}: ask={best_ask}, bid={best_bid}, asks={len(asks)}, bids={len(bids)}"
        print("  ", summarize(book_yes, "yes_id"))
        print("  ", summarize(book_no, "no_id"))

asyncio.run(test())
