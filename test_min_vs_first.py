import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=20)
    print("markets:", len(markets))
    for m in markets[:5]:
        print(m.question[:60], "liq", m.liquidity, m.clob_token_ids)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets[:5]]
    books = await api.fetch_order_books_batch(token_pairs)
    for m, (yes_book, no_book) in zip(markets[:5], books):
        if not yes_book or not no_book:
            print("missing book")
            continue
        yes_asks = yes_book.asks
        no_asks = no_book.asks
        if not yes_asks or not no_asks:
            continue
        yes_min = min(float(a['price']) for a in yes_asks)
        no_min = min(float(a['price']) for a in no_asks)
        yes_first = float(yes_asks[0]['price'])
        no_first = float(no_asks[0]['price'])
        total_min = yes_min + no_min
        total_first = yes_first + no_first
        print(f"{m.question[:40]} | min sum {total_min:.3f} ({yes_min:.3f}+{no_min:.3f}) | first sum {total_first:.3f}")

asyncio.run(test())
