import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    for m in markets:
        print("Market:", m.question[:60])
        print("  outcome_prices:", m.outcome_prices)
        yes_id, no_id = m.clob_token_ids
        book_yes = await api.fetch_order_book(yes_id)
        book_no = await api.fetch_order_book(no_id)
        if book_yes and book_yes.asks:
            best_ask_yes = min(float(a['price']) for a in book_yes.asks)
        else:
            best_ask_yes = None
        if book_no and book_no.asks:
            best_ask_no = min(float(a['price']) for a in book_no.asks)
        else:
            best_ask_no = None
        if best_ask_yes and best_ask_no:
            total = best_ask_yes + best_ask_no
            print(f"  sum={total:.3f}, yes_ask={best_ask_yes:.3f}, no_ask={best_ask_no:.3f}")
            if total <= 1.005:
                print("  -> near bracket!")

asyncio.run(test())
