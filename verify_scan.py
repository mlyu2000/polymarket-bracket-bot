import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging = __import__('logging')
logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    markets = await api.fetch_active_markets()
    print('markets', len(markets))
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    print('books', len(all_books))
    opps = []
    near_misses = []
    for i, (m, (yes_book, no_book)) in enumerate(zip(markets, all_books)):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # Use first ask as per script
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50]))
    print('opps', len(opps))
    print('near', len(near_misses))
    if near_misses:
        for t,q in near_misses[:10]:
            print(t,q)

asyncio.run(scan())
