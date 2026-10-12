import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    print(f"Fetched {len(markets)} markets")
    count_both = 0
    count_one = 0
    for m in markets:
        yes_id = m.clob_token_ids[0]
        no_id = m.clob_token_ids[1]
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        yes_has = bool(yes_book and yes_book.asks)
        no_has = bool(no_book and no_book.asks)
        if yes_has and no_has:
            count_both += 1
            print("BOTH:", m.question[:80])
        elif yes_has or no_has:
            count_one += 1
        await asyncio.sleep(0.1)
        if count_both >= 5:
            break
    print(f"Both books: {count_both}, One book: {count_one}")

asyncio.run(test())
