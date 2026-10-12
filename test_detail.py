import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test_specific_detail():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=1000)
    target = None
    for m in markets:
        if "Alexander Hägg" in m.question:
            target = m
            break
    if not target:
        print("not found")
        return
    print("found", target.question)
    yes_book = await api.fetch_order_book(target.clob_token_ids[0])
    no_book = await api.fetch_order_book(target.clob_token_ids[1])
    yes_min = min(float(a['price']) for a in yes_book.asks)
    no_min = min(float(a['price']) for a in no_book.asks)
    yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
    no_ask = min(no_book.asks, key=lambda a: float(a['price']))
    print("yes min", yes_min, "ask", yes_ask)
    print("no min", no_min, "ask", no_ask)
    print("yes volume int", int(float(yes_ask['size'])))
    print("no volume int", int(float(no_ask['size'])))
    opp = detector.detect(target, yes_book, no_book)
    print("detector returned", opp)
    if opp:
        print("opp details", opp.yes_price, opp.no_price, opp.total_cost, opp.net_edge, opp.max_shares)

asyncio.run(test_specific_detail())
