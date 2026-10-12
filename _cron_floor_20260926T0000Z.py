import asyncio, json, logging, time
from datetime import datetime, timezone
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def full():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    all_totals = []
    priced = 0
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        all_totals.append((total, m.question[:50], m.liquidity))
        if total < 1.0:
            brackets.append((total, m.question[:50], ya, na, m.liquidity))
        elif total <= 1.005:
            rows.append((round(total, 3), m.question[:50], ya, na, m.liquidity))
    rows.sort()
    brackets.sort()
    all_totals.sort()
    return {'markets': len(markets), 'priced': priced, 'brackets': brackets,
            'near': rows, 'floor': [round(t, 3) for t, _, _ in all_totals[:3]], 'dt': dt}

r = asyncio.run(full())
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + 'Z'
out = {
    "run_ts_utc": ts, "markets": r['markets'], "priced": r['priced'],
    "scan_time_s": round(r['dt'], 1), "brackets": r['brackets'],
    "near_misses_asks0": 0, "near_misses_bestask": r['near'],
    "best_floor": r['floor'],
    "note": "asks[0] is worst ask (DESC sort) -> verbatim near-miss block under-reports; best-ask authoritative"
}
path = f"runs/scan_{ts}.json"
with open(path, "w") as f:
    json.dump(out, f)
print(f"saved {path}")
print(f"priced={r['priced']}/{r['markets']} brackets={len(r['brackets'])} near={len(r['near'])} floor={r['floor']}")
for row in r['near']:
    print(f"  {row[0]:.3f} | Yes@{row[2]:.3f} No@{row[3]:.3f} | liq={row[4]:.0f} | {row[1]}")
