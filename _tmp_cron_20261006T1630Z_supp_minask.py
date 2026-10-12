# Supplementary: near-misses using BEST asks (min price), since CLOB /book
# returns asks in descending order — asks[0] is the WORST ask (~0.999).
import asyncio, logging
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if floor is None or total < floor[0]:
                floor = (total, m.question[:60], yp, np_, m.liquidity)
            if 0 < total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity, opp is not None))

    near.sort()
    print(f"priced markets: {priced}")
    if floor:
        print(f"global min sum(best asks): {floor[0]:.4f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | {floor[1]}")
    print(f"best-ask near-misses (<=1.005): {len(near)}")
    for t, q, yp, np_, liq, flagged in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | det={'YES' if flagged else 'no'} | {q}")

asyncio.run(scan())
