import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    exact = 0
    bracket_min = []
    near = []
    no_asks = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            exact += 1
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if total < 1.0:
                bracket_min.append((total, m.question[:60], yp, np, m.liquidity))
            elif total <= 1.005:
                near.append((total, m.question[:50], yp, np, m.liquidity))
        else:
            no_asks += 1

    bracket_min.sort()
    near.sort()
    print(f"markets={len(markets)} detector_hits={exact} books_missing_asks={no_asks}")
    print(f"BEST-ASK BRACKETS (min sum < 1.00): {len(bracket_min)}")
    for t, q, yp, np, liq in bracket_min[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"BEST-ASK NEAR-MISSES (1.000-1.005): {len(near)}")
    for t, q, yp, np, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    sums = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            sums.append(min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks))
    if sums:
        sums.sort()
        print(f"priced={len(sums)} floor={sums[0]:.4f} p5={sums[min(4,len(sums)-1)]:.4f} median={sums[len(sums)//2]:.4f}")

asyncio.run(supp())
