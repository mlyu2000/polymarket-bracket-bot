import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    count=0
    best=[]
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_best = min(yes_book.asks, key=lambda a: float(a['price']))
        no_best = min(no_book.asks, key=lambda a: float(a['price']))
        total = float(yes_best['price']) + float(no_best['price'])
        if total < 1.0:
            count+=1
            best.append((total, m.question[:80]))
        if total < 1.005:
            # print for debug
            pass
    print('brackets <1.0:', count)
    # find lowest totals
    totals=[]
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_best = min(yes_book.asks, key=lambda a: float(a['price']))
        no_best = min(no_book.asks, key=lambda a: float(a['price']))
        total = float(yes_best['price']) + float(no_best['price'])
        totals.append((total, m.question[:80], float(yes_best['price']), float(no_best['price'])))
    totals.sort()
    for t in totals[:20]:
        print(f"{t[0]:.4f} yes {t[2]:.4f} no {t[3]:.4f} | {t[1]}")

asyncio.run(find())
