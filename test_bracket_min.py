import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=100)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    count=0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb: continue
        if not yb.asks or not nb.asks: continue
        # simulate detector logic
        yes_ask = min(yb.asks, key=lambda a: float(a["price"]))
        no_ask = min(nb.asks, key=lambda a: float(a["price"]))
        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])
        total = yes_price + no_price
        if total < 1.0:
            print(f"BRACKET! {total:.4f} yes={yes_price:.3f} no={no_price:.3f} {m.question[:60]}")
            count+=1
        elif total <= 1.005:
            # near miss
            pass
    print(f"Total brackets found: {count}")

asyncio.run(test())
