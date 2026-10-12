import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    print(f"fetched {len(markets)} markets")
    hits = 0
    for m in markets:
        q = m.question.lower()
        if ('new hampshire' in q or 'house' in q and 'seat' in q
                or 'amsterdam' in q or '13c' in q or '13°' in q
                or 'nh-02' in q or 'bolsonaro' in q or 'levante' in q or 'hormuz' in q):
            hits += 1
            token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
            books = await api.fetch_order_books_batch(token_pairs)
            yes_book, no_book = books[0]
            ya = [float(a['price']) for a in (yes_book.asks or [])] if yes_book else []
            na = [float(a['price']) for a in (no_book.asks or [])] if no_book else []
            if ya and na:
                print(f"{m.question[:70]} | minY={min(ya):.3f} minN={min(na):.3f} sum={min(ya)+min(na):.4f} liq={m.liquidity}")
            else:
                print(f"{m.question[:70]} | yes_asks={len(ya)} no_asks={len(na)} liq={m.liquidity}")
    print(f"hits={hits}")

asyncio.run(check())
