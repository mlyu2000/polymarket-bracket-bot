import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def debug_no_book():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    for m, (yes_book, no_book) in zip(markets, books):
        if m.question == "Will Alexander Hägg be the next Regional Board Chair of Region Gävleborg?":
            print("market found")
            print("yes_book:", yes_book)
            print("no_book:", no_book)
            if yes_book and no_book:
                yes_min = min(yes_book.asks, key=lambda a: float(a['price']))
                no_min = min(no_book.asks, key=lambda a: float(a['price']))
                print("yes_min", yes_min)
                print("no_min", no_min)
                yes_vol = int(float(yes_min['size']))
                no_vol = int(float(no_min['size']))
                print("volumes", yes_vol, no_vol)
                total = float(yes_min['price']) + float(no_min['price'])
                print("total", total)
                opp = detector.detect(m, yes_book, no_book)
                print("opp", opp)
                if opp:
                    print("opp details", opp.yes_price, opp.no_price, opp.net_edge, opp.max_shares)
            break

asyncio.run(debug_no_book())
