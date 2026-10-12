import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor
import logging
logging.basicConfig(level=logging.ERROR)

async def scan_debug():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=20)
    print(f"Markets fetched: {len(markets)}")
    for i,m in enumerate(markets[:10]):
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # Find best asks
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            yes_price = float(yes_ask['price'])
            no_price = float(no_ask['price'])
            total = yes_price + no_price
            print(f"{i}: total={total:.4f} yes={yes_price:.3f} no={no_price:.3f} q={m.question[:60]}")
            opp = detector.detect(m, yes_book, no_book)
            if opp:
                print("  OPPORTUNITY FOUND:", opp.total_cost, opp.net_edge)

asyncio.run(scan_debug())
