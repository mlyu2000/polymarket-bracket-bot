import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find_low():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    low = []
    for m, (yes,no) in zip(markets, books):
        if yes and no and yes.asks and no.asks:
            y0 = float(yes.asks[0]['price'])
            n0 = float(no.asks[0]['price'])
            if y0 < 0.5 or n0 < 0.5:
                low.append((y0,n0,m.question[:60]))
    print('low count', len(low))
    for x in low[:20]:
        print(x)

asyncio.run(find_low())
