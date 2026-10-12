import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yb = await api.fetch_order_book(yes_id)
        nb = await api.fetch_order_book(no_id)
        print("Market:", m.question[:60])
        print("Liquidity:", m.liquidity)
        if yb and nb:
            y_ask_min = min(float(a['price']) for a in yb.asks)
            n_ask_min = min(float(a['price']) for a in nb.asks)
            print(f"Best asks: Yes {y_ask_min} No {n_ask_min} sum {y_ask_min+n_ask_min}")
            opp = detector.detect(m, yb, nb)
            print("Opp:", opp)
        print("---")
asyncio.run(test())
