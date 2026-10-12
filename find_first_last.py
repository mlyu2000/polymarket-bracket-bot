import asyncio
from polymarket_api import PolymarketAPI
from config import Config

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    count=0
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # Try both first and last
            first_yes = float(yes_book.asks[0]['price'])
            first_no = float(no_book.asks[0]['price'])
            last_yes = float(yes_book.asks[-1]['price'])
            last_no = float(no_book.asks[-1]['price'])
            s_first = first_yes + first_no
            s_last = last_yes + last_no
            if s_first < 1.0 or s_last < 1.0:
                print("FOUND", m.question[:80])
                print("first", first_yes, first_no, s_first)
                print("last", last_yes, last_no, s_last)
                count+=1
                break
        await asyncio.sleep(0.02)
    print("count",count)

asyncio.run(f())
