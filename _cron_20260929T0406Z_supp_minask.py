import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        priced += 1
        ymin = min(float(a['price']) for a in yb.asks)
        nmin = min(float(a['price']) for a in nb.asks)
        rows.append((ymin + nmin, ymin, nmin, m.question[:60], m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}/{len(markets)}")
    print("top-8 best true min-ask sums:")
    for s, y, n, q, liq in rows[:8]:
        print(f"  {s:.3f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
    print(f"count sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    with open(f'runs/bracket_scan_{ts}.json', 'w') as f:
        json.dump({'ts': ts, 'markets': len(markets), 'priced': priced,
                   'brackets': 0, 'top_min_ask_sums': rows[:10]}, f, indent=1)

asyncio.run(supp())
