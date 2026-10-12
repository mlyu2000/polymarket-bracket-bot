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
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
n = len(rows)
print(f"best-ask floor scan: {n} priced markets")
print(f"min sum = {rows[0][0]:.4f} | count < 1.00: {sum(1 for r in rows if r[0] < 1.00)} | count <= 1.001: {sum(1 for r in rows if r[0] <= 1.001)} | count <= 1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
print("--- top 8 lowest best-ask sums ---")
for total, q, yp, np_, liq in rows[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
