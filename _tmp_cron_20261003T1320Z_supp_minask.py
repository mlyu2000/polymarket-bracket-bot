import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    skipped = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not (m.active and not m.closed) or m.liquidity <= 0:
            skipped += 1
            continue
        if not yb or not nb or not yb.asks or not nb.asks:
            skipped += 1
            continue
        yp = min(float(a['price']) for a in yb.asks)
        npr = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or npr <= 0 or yp >= 1.0 or npr >= 1.0:
            skipped += 1
            continue
        rows.append((round(yp + npr, 4), m.question[:60], yp, npr, m.liquidity))
    rows.sort()
    return dt, skipped, rows

dt, skipped, rows = asyncio.run(scan())
print(f"best-ask scan: {len(rows)} priced markets, {skipped} skipped, {dt:.1f}s")
print("global floor (min best-ask sum):", rows[0][0] if rows else None)
for t, q, yp, npr, liq in rows[:10]:
    print(f"  sum={t:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
print("count sum<1.00 :", sum(1 for r in rows if r[0] < 1.00))
print("count sum<=1.005:", sum(1 for r in rows if r[0] <= 1.005))
with open('_tmp_cron_20261003T1320Z_supp_data.json', 'w') as f:
    json.dump(rows[:20], f)
