import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # Use best ask (minimum price)
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            yes_price = float(yes_ask['price'])
            no_price = float(no_ask['price'])
            total = yes_price + no_price
            sums.append((total, m.question[:60], m.liquidity))
    
    sums.sort(key=lambda x: x[0])
    print(f"Checked {len(sums)} markets")
    print("Top 20 lowest sums:")
    for s in sums[:20]:
        print(f"{s[0]:.4f} | liq={s[2]:.0f} | {s[1]}")

asyncio.run(scan())
