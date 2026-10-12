import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def check():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    for m in markets:
        if 'Apple' in m.question and 'largest' in m.question.lower():
            pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
            books = await api.fetch_order_books_batch(pairs)
            yes_book, no_book = books[0]
            if yes_book and no_book and yes_book.asks and no_book.asks:
                ya = min(float(a['price']) for a in yes_book.asks)
                na = min(float(a['price']) for a in no_book.asks)
                print(f"FOUND: {m.question[:70]} | yes_min={ya} no_min={na} sum={ya+na:.3f} liq={m.liquidity}")
            else:
                print(f"FOUND but unpriced: {m.question[:70]} liq={m.liquidity}")
            return
    print("Apple-largest-company market no longer in active set")

asyncio.run(check())
