import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan_small():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=20)
    print(f"Markets fetched: {len(markets)}")
    total = 0
    for m in markets:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book:
            # find min asks
            yes_asks = [float(a['price']) for a in yes_book.asks]
            no_asks = [float(a['price']) for a in no_book.asks]
            if yes_asks and no_asks:
                min_yes = min(yes_asks)
                min_no = min(no_asks)
                s = min_yes + min_no
                print(f"{m.question[:50]} | min yes={min_yes:.3f} min no={min_no:.3f} sum={s:.3f} liq={m.liquidity}")
                total += 1
    print("Checked", total)

asyncio.run(scan_small())
