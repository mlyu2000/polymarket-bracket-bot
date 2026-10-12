import asyncio, logging
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            sums.append(total)
            if total <= 1.005:
                rows.append((total, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    sums.sort()
    floor = sums[0] if sums else None
    return priced, rows, floor, sums[:5] if sums else []

priced, rows, floor, low5 = asyncio.run(scan())
print(f"min-ask floor check: {len(rows)} markets with best-ask sum <= 1.005 (of {priced} priced)")
print(f"global floor sum = {floor}; 5 lowest = {[f'{s:.3f}' for s in low5]}")
for total, q, yp, npz, liq in rows[:10]:
    print(f"  [M] {total:.3f} | Yes@{yp:.3f} No@{npz:.3f} | liq={liq} | {q}")
