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

    rows = []
    brackets_min = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        rows.append((total, m.question[:60], ya, na, m.liquidity))
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets_min.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))

    rows.sort()
    return rows, brackets_min, len(markets)

rows, brackets, n = asyncio.run(scan())
print(f"Markets: {n} | best-ask (min) sums analyzed: {len(rows)}")
print(f"TRUE BRACKETS (detector min-ask sum < 1.00): {len(brackets)}")
for s, e, sh, q, liq in sorted(brackets):
    print(f"  sum={s:.3f} edge={e:.4f} shares={sh} liq={liq} | {q}")
print("Top 8 lowest min-ask sums:")
for total, q, ya, na, liq in rows[:8]:
    print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
if rows:
    print(f"Global floor (min-ask): {rows[0][0]:.3f}")
