import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def floor_check():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = 0
    true_near = []
    best = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(yes_book.asks, key=lambda a: float(a['price']))
        na = min(no_book.asks, key=lambda a: float(a['price']))
        yp, np_ = float(ya['price']), float(na['price'])
        total = yp + np_
        priced += 1
        liq_shares = min(int(float(ya['size'])), int(float(na['size'])))
        row = (total, m.question[:70], yp, np_, m.liquidity, liq_shares)
        if best is None or total < best[0]:
            best = row
        if total <= 1.005:
            true_near.append(row)

    true_near.sort()
    print(f"Markets with both books priced: {priced}")
    if best:
        print(f"TRUE FLOOR: sum={best[0]:.3f} Yes@{best[2]:.3f} No@{best[3]:.3f} liq_shares={best[5]} | {best[1]}")
    print(f"TRUE near-misses (min-ask sum<=1.005): {len(true_near)}")
    for total, q, yp, np_, liq, ls in true_near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | matched_shares={ls} | {q}")

asyncio.run(floor_check())
