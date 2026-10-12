import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    brackets = []
    near = []
    priced = 0
    floor = (9.9, None)
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        if total < floor[0]:
            floor = (total, m.question[:60])
        if total < 1.00 and m.liquidity > 0:
            brackets.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:50], yp, np_, m.liquidity))

    brackets.sort()
    near.sort()
    print(f"SUPP best-ask (min): {priced}/{len(markets)} markets with both-sided asks")
    print(f"SUPP true brackets (best-ask sum < 1.00, liq>0): {len(brackets)}")
    for t, q, yp, np_, liq in brackets[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"SUPP near-misses (1.00<=sum<=1.005, best-ask): {len(near)}")
    for t, q, yp, np_, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"SUPP global best-ask floor: {floor[0]:.4f} | {floor[1]}")

asyncio.run(supp())
