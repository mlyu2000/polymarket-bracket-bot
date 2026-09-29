import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best = []
    priced = 0
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        priced += 1
        total = yp + np
        if total < 1.0 and m.active and not m.closed and m.liquidity > 0:
            opp = detector.detect(m, yes_book, no_book)
            if opp:
                brackets.append(opp)
        best.append((total, m.question[:60], yp, np, m.liquidity))
    best.sort()
    print(f"Priced markets: {priced}")
    print(f"Min-ask sum floor: {best[0][0]:.4f}" if best else "no data")
    print("Top 8 best-ask sums:")
    for t, q, yp, np, liq in best[:8]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    nm = [b for b in best if b[0] <= 1.005]
    print(f"Best-ask near-misses (<=1.005): {len(nm)}")

asyncio.run(supp())
