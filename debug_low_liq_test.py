import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    print(f"markets {len(markets)}")
    # filter by liquidity
    low_liq = [m for m in markets if m.liquidity < 5000]
    print(f"low liq <5000: {len(low_liq)}")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in low_liq[:100]]
    all_books = await api.fetch_order_books_batch(token_pairs)
    near = []
    for m,(y,n) in zip(low_liq[:100], all_books):
        if y and n and y.asks and n.asks:
            yes_ask = min(y.asks, key=lambda a: float(a["price"]))
            no_ask = min(n.asks, key=lambda a: float(a["price"]))
            total = float(yes_ask["price"])+float(no_ask["price"])
            if total <= 1.005:
                near.append((total, m.question[:60]))
    print("near misses", len(near))
    for t,q in near[:10]:
        print(t,q)

asyncio.run(test())
