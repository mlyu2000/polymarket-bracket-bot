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

    opps = []
    best_totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            best_totals.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    best_totals.sort()
    return len(markets), opps, best_totals

n, opps, best_totals = asyncio.run(scan())
print(f"MARKETS: {n}")
print(f"BEST-ASK BRACKETS (sum<1.00): {sum(1 for t in best_totals if t[0] < 1.00)}")
print(f"FLOOR (min best-ask sum): {best_totals[0][0]:.4f} | {best_totals[0][1]}")
print("BEST-ASK NEAR-MISSES (<=1.005):")
for total, q, yp, np_, liq in best_totals:
    if total <= 1.005:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
