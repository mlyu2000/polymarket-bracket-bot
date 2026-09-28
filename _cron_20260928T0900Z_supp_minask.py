# Supplementary: TRUE best-ask (min) near-misses + floor. The verbatim cron
# near-miss block uses asks[0], which on the CLOB is the WORST ask (asks are
# DESC-sorted) — known to overstate totals. detector.py itself uses min()
# correctly, so BRACKETS output is unaffected.
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    priced = 0
    rows = []
    floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if floor is None or total < floor:
                floor = total
                floor_q = m.question[:60]
            if total <= 1.005:
                rows.append((total, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return len(markets), priced, floor, floor_q, rows

res = asyncio.run(scan())
print(f"min-ask scan: {res[0]} markets, {res[1]} with priced books both sides")
print(f"TRUE floor (min-ask sum): {res[2]:.4f} | {res[3]}")
print(f"min-ask near-misses (<=1.005): {len(res[4])}")
for total, q, yp, np_, liq in res[4][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
