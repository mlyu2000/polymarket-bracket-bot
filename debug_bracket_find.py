import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    brackets = []
    for m,(y,n) in zip(markets, all_books):
        if y and n and y.asks and n.asks:
            yes_min = min(y.asks, key=lambda a: float(a["price"]))
            no_min = min(n.asks, key=lambda a: float(a["price"]))
            total = float(yes_min["price"])+float(no_min["price"])
            if total < 1.0:
                brackets.append((total, m.question[:80], m.liquidity, float(yes_min["price"]), float(no_min["price"])))
    print("brackets <1", len(brackets))
    for t,q,liq,yp,np in sorted(brackets)[:20]:
        print(t, yp, np, liq, q)

asyncio.run(test())
