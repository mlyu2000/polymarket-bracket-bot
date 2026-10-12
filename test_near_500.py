import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    count = 0
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        book_yes = await api.fetch_order_book(yes_id)
        book_no = await api.fetch_order_book(no_id)
        if book_yes and book_no and book_yes.asks and book_no.asks:
            best_ask_yes = min(float(a['price']) for a in book_yes.asks)
            best_ask_no = min(float(a['price']) for a in book_no.asks)
            total = best_ask_yes + best_ask_no
            if total <= 1.005:
                print(f"{total:.3f} | {m.question[:60]}")
                count += 1
    print("Total near:", count)

asyncio.run(test())
