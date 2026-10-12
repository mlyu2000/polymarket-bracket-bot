import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    target = "Will Pogon Szczecin win on 2026-08-23"
    for m in markets:
        if target in m.question:
            print("Found market")
            print(m.question)
            yes_id = m.clob_token_ids[0]
            no_id = m.clob_token_ids[1]
            yes_book = await api.fetch_order_book(yes_id)
            no_book = await api.fetch_order_book(no_id)
            print("yes best ask:", min(yes_book.asks, key=lambda a: float(a["price"])) if yes_book and yes_book.asks else None)
            print("no best ask:", min(no_book.asks, key=lambda a: float(a["price"])) if no_book and no_book.asks else None)
            opp = detector.detect(m, yes_book, no_book)
            if opp:
                print("OPP FOUND", opp.total_cost, opp.net_edge)
            else:
                print("NO OPP")
                # manual calc
                yes_price = float(min(yes_book.asks, key=lambda a: float(a["price"]))["price"])
                no_price = float(min(no_book.asks, key=lambda a: float(a["price"]))["price"])
                total = yes_price + no_price
                print(f"Manual sum: {yes_price}+{no_price}={total}")
            break

asyncio.run(test())
