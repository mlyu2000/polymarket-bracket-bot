import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    
    markets = await api.fetch_active_markets(limit=500)
    print(f"Markets fetched: {len(markets)}")
    
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    
    for m, (yes_book, no_book) in zip(markets[:20], all_books[:20]):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        
        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])
        total = yes_price + no_price
        
        if total <= 1.005:
            print(f"{total:.3f} | {m.question[:50]} | liq={m.liquidity}")

asyncio.run(scan())
