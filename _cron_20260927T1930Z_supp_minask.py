# Supplementary: near-misses computed with the TRUE best ask (min price),
# since CLOB /book asks are DESC-sorted and asks[0] is the worst ask.
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best = []
    priced = 0
    detected = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            detected += 1
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            best.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    best.sort()
    print(f"markets={len(markets)} priced_by_both_asks={priced} detector_opps={detected}")
    print("TRUE-BEST-ASK top 10 totals (yes_ask_min + no_ask_min):")
    for total, q, yp, np_, liq in best[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"min_total={best[0][0]:.4f}" if best else "no priced markets")

asyncio.run(scan())
