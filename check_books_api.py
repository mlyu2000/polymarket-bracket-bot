import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    for m in markets:
        print(m.question[:80])
        print('clob_token_ids', m.clob_token_ids)
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if yes_book:
            print('yes asks', yes_book.asks[:2])
        if no_book:
            print('no asks', no_book.asks[:2])
        print('---')

asyncio.run(main())
