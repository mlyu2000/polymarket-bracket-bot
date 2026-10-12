import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    print('markets', len(markets))
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets[:10]]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for i,(m,(yes_book,no_book)) in enumerate(zip(markets[:10], all_books)):
        print('market', i, m.question[:60])
        print('yes asks', yes_book.asks[:2] if yes_book else None)
        print('no asks', no_book.asks[:2] if no_book else None)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = float(yes_book.asks[0]['price'])
            no_price = float(no_book.asks[0]['price'])
            total = yes_price + no_price
            print('total', total)

asyncio.run(scan())
