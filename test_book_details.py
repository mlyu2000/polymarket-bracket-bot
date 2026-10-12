import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        print(m.question[:80])
        print('  clob ids', m.clob_token_ids)
        # fetch both books
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        print('  yes asks', len(yes_book.asks) if yes_book else None, 'bids', len(yes_book.bids) if yes_book else None)
        print('  no asks', len(no_book.asks) if no_book else None, 'bids', len(no_book.bids) if no_book else None)
        # print sample
        if yes_book and yes_book.asks:
            print('  yes best ask', yes_book.asks[0])
        if no_book and no_book.asks:
            print('  no best ask', no_book.asks[0])
        if yes_book and yes_book.bids:
            print('  yes best bid', yes_book.bids[0])
        if no_book and no_book.bids:
            print('  no best bid', no_book.bids[0])
        print('---')

asyncio.run(test())
