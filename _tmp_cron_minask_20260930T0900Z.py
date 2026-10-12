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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))

    rows.sort()
    return markets, rows

markets, rows = asyncio.run(scan())
n_priced = len(rows)
lt1 = [r for r in rows if r[0] < 1.0]
nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"SUPP (true best asks, min()): {len(markets)} markets, {n_priced} priced")
print(f"TRUE BRACKETS (sum<1.00): {len(lt1)}")
for s, q, yp, np_, liq in lt1[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"NEAR-MISS (1.000-1.005): {len(nm)}")
for s, q, yp, np_, liq in nm[:10]:
    print(f"  {s:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if rows:
    print(f"GLOBAL BEST SUM: {rows[0][0]:.4f} | {rows[0][1]}")
