import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check_books():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    for m in markets:
        print(m.question[:80])
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        y,n = books[0]
        if y and n:
            y_asks = [a['price'] for a in y.asks[:5]]
            n_asks = [a['price'] for a in n.asks[:5]]
            print(" yes asks", y_asks)
            print(" no asks ", n_asks)
            print(" min yes", min(float(p) for p in y_asks))
            print(" min no ", min(float(p) for p in n_asks))
        print("---")

asyncio.run(check_books())
