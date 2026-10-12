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

    opps = []
    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            # TRUE best asks: asks are DESC-sorted, so min() = best ask
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if total <= 1.005:
                near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    return markets, opps, near, priced

async def main():
    markets, opps, near, priced = await scan()
    print(f"markets={len(markets)} priced_pairs={priced} detector_opps={len(opps)}")
    print(f"TRUE near-misses (best-ask sum <= 1.005): {len(near)}")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if near:
        print(f"best floor seen this scan: {near[0][0]:.4f}")

asyncio.run(main())
