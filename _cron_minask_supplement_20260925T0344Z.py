import asyncio, logging, time, json, os
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
    elapsed = time.time() - t0

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    return rows, elapsed

rows, elapsed = asyncio.run(scan())
print(f"🧮 min-ask floor scan: {len(rows)} priced markets in {elapsed:.1f}s")
brackets = [r for r in rows if r[0] < 1.0]
print(f"✅ BRACKETS (min-ask sum < 1.00): {len(brackets)}")
for s, q, yp, np_, liq in brackets[:10]:
    print(f"  🔴 {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print("Top-5 closest (min-ask):")
for s, q, yp, np_, liq in rows[:5]:
    print(f"  {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

os.makedirs('runs', exist_ok=True)
ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
with open(f'runs/minask_floor_{ts}.json', 'w') as f:
    json.dump({'timestamp_utc': ts, 'priced_markets': len(rows),
               'brackets': [ {'sum': s, 'question': q, 'yes': y, 'no': n, 'liquidity': l} for s,q,y,n,l in brackets ],
               'closest': [ {'sum': s, 'question': q, 'yes': y, 'no': n, 'liquidity': l} for s,q,y,n,l in rows[:10] ]}, f, indent=2)
print(f"persisted -> runs/minask_floor_{ts}.json")
