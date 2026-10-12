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

    rows = []
    detected = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            detected.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            rows.append((ya + na, m.question[:50], ya, na, m.liquidity))
    rows.sort()
    return detected, rows

detected, rows = asyncio.run(scan())
print(f"Detector BRACKETS: {len(detected)}")
for s, e, sh, q, liq in detected:
    print(f"  sum={s:.4f} edge={e:.4f} shares={sh} liq={liq} | {q}")
print(f"Best min-ask totals (top 10 of {len(rows)} priced):")
for total, q, ya, na, liq in rows[:10]:
    flag = "LT1" if total < 1.0 else ""
    print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {flag} {q}")
n_lt1 = sum(1 for r in rows if r[0] < 1.0)
n_le1005 = sum(1 for r in rows if r[0] <= 1.005)
print(f"min-ask totals < 1.000: {n_lt1} | <= 1.005: {n_le1005}")
