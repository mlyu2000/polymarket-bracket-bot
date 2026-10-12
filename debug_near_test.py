import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=20)
    print(f"fetched {len(markets)}")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    count = 0
    for m,(y,n) in zip(markets, all_books):
        if y and n and y.asks and n.asks:
            yes_ask = min(y.asks, key=lambda a: float(a["price"]))
            no_ask = min(n.asks, key=lambda a: float(a["price"]))
            yp = float(yes_ask["price"])
            np = float(no_ask["price"])
            total = yp+np
            if total <= 1.005:
                count += 1
                print("NEAR", total, m.question[:60], yp, np, m.liquidity)
    print("near count", count)

asyncio.run(test())
