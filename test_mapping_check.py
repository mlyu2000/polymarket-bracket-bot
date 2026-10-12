import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    for m in markets:
        print("Market:", m.question[:60])
        print("  outcomes:", m.outcomes)
        print("  outcome_prices:", m.outcome_prices)
        yes_id, no_id = m.clob_token_ids
        book_yes = await api.fetch_order_book(yes_id)
        book_no = await api.fetch_order_book(no_id)
        if book_yes:
            asks_yes = [float(a['price']) for a in book_yes.asks] if book_yes.asks else []
            bids_yes = [float(b['price']) for b in book_yes.bids] if book_yes.bids else []
            print("  yes_id asks:", asks_yes[:3], "bids:", bids_yes[:3])
        if book_no:
            asks_no = [float(a['price']) for a in book_no.asks] if book_no.asks else []
            bids_no = [float(b['price']) for b in book_no.bids] if book_no.bids else []
            print("  no_id asks:", asks_no[:3], "bids:", bids_no[:3])
        # Check mapping: if yes_id has asks near outcome_prices[0]? 
        # For market with outcome_prices [0.0005, 0.9995], yes price should be ~0.0005
        # So best ask for yes token should be near 0.0005? But we see best ask 0.999 for yes_id
        # Maybe token ids are reversed: yes_id actually corresponds to NO?
        print("  -> mapping check")
        break

asyncio.run(test())
