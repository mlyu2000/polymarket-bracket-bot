import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    elapsed = time.time() - t0

    # Correct floor using MIN over asks (asks are DESC-sorted: asks[0]=worst)
    best = []
    brackets = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            best.append((total, m.question[:60], yp, np, m.liquidity))
    best.sort()
    print(f"[minask] {len(markets)} markets, {priced} priced, {elapsed:.1f}s")
    print(f"[minask] detector brackets: {len(brackets)}")
    if best:
        print(f"[minask] floor sum: {best[0][0]:.4f} | Yes@{best[0][2]:.3f} No@{best[0][3]:.3f} | liq={best[0][4]} | {best[0][1]}")
    for total, q, yp, np, liq in best[:5]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
