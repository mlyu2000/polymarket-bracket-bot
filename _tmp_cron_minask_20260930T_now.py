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

    true_near = []   # min-ask based (correct best ask)
    detected = 0
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            detected += 1
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_min = min(float(a['price']) for a in yes_book.asks)
            no_min = min(float(a['price']) for a in no_book.asks)
            total = yes_min + no_min
            sums.append(total)
            if total <= 1.005:
                true_near.append((total, m.question[:50], yes_min, no_min, m.liquidity))

    true_near.sort()
    print(f"Markets: {len(markets)} | detector-brackets: {detected} | min-ask near-misses (<=1.005): {len(true_near)}")
    if sums:
        print(f"Best min-ask sum across all markets: {min(sums):.4f}")
    for total, q, yp, np, liq in true_near[:5]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
