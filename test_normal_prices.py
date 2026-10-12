import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    # Find a market with normal prices ~0.5
    markets = await api.fetch_active_markets(limit=100)
    for m in markets:
        if m.outcome_prices[0] > 0.1 and m.outcome_prices[0] < 0.9:
            print("Found market:", m.question[:60])
            print("  outcomes:", m.outcomes)
            print("  outcome_prices:", m.outcome_prices)
            yes_id, no_id = m.clob_token_ids
            book_yes = await api.fetch_order_book(yes_id)
            book_no = await api.fetch_order_book(no_id)
            if book_yes:
                asks_yes = [float(a['price']) for a in book_yes.asks] if book_yes.asks else []
                bids_yes = [float(b['price']) for b in book_yes.bids] if book_yes.bids else []
                print("  yes_id asks best:", min(asks_yes) if asks_yes else None, "bids best:", max(bids_yes) if bids_yes else None)
            if book_no:
                asks_no = [float(a['price']) for a in book_no.asks] if book_no.asks else []
                bids_no = [float(b['price']) for b in book_no.bids] if book_no.bids else []
                print("  no_id asks best:", min(asks_no) if asks_no else None, "bids best:", max(bids_no) if bids_no else None)
            break

asyncio.run(test())
