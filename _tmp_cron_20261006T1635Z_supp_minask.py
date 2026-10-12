import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    priced = 0
    floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            continue
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if floor is None or total < floor:
                floor = total
            if total <= 1.005:
                near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    return markets, priced, floor, near

markets, priced, floor, near = asyncio.run(scan())
print(f"MIN-ASK supplement: {len(markets)} markets, {priced} priced books, floor sum={floor}")
print(f"TRUE near-misses (min-ask sum <= 1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
