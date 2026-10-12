import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    for m in markets:
        # skip low liquidity
        if m.liquidity < 10000:
            continue
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if not yes_book or not no_book:
            continue
        # get best ask (lowest price)
        try:
            yes_best = min(float(a['price']) for a in yes_book.asks)
            no_best = min(float(a['price']) for a in no_book.asks)
        except:
            continue
        total = yes_best + no_best
        if 0.9 < total < 1.1:
            print(m.question[:80])
            print("  yes best ask", yes_best, "no best ask", no_best, "sum", total)
            print("  last trade", yes_book.last_trade_price, no_book.last_trade_price)
            print()

asyncio.run(find())
