import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=5)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m,(y,n) in zip(markets, all_books):
        print("---")
        print(m.question[:80])
        print("liquidity", m.liquidity)
        if y and n and y.asks and n.asks:
            yes_ask = min(y.asks, key=lambda a: float(a["price"]))
            no_ask = min(n.asks, key=lambda a: float(a["price"]))
            yp = float(yes_ask["price"])
            np = float(no_ask["price"])
            total = yp+np
            print("yes", yp, yes_ask)
            print("no", np, no_ask)
            print("total", total)
            opp = detector.detect(m, y, n)
            print("opp", opp)
        else:
            print("no books")

asyncio.run(test())
