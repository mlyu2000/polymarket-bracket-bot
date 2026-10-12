import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test_detector():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=10)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    for m, (yes,no) in zip(markets, books):
        opp = detector.detect(m, yes, no)
        print(m.question[:60], 'opp', opp)
        if yes and no and yes.asks and no.asks:
            y_min = min(yes.asks, key=lambda a: float(a['price']))
            n_min = min(no.asks, key=lambda a: float(a['price']))
            total = float(y_min['price'])+float(n_min['price'])
            print('  min sum', total)

asyncio.run(test_detector())
