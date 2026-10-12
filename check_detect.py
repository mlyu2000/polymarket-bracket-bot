import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)}")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    opps = []
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append(opp)
        else:
            if yb and nb and yb.asks and nb.asks:
                yes_ask = min(yb.asks, key=lambda a: float(a['price']))
                no_ask = min(nb.asks, key=lambda a: float(a['price']))
                total = float(yes_ask['price']) + float(no_ask['price'])
                if total < 1.01:
                    print(f"{total:.4f} | {m.question[:70]} | liq={m.liquidity} | yes_ask={yes_ask['price']} no_ask={no_ask['price']}")

    print(f"\nOpportunities found: {len(opps)}")

asyncio.run(test())
