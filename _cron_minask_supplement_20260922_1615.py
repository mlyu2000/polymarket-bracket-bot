import asyncio, json, logging, time
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
    t0 = time.time()
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    priced = 0
    brackets = []
    near = []
    best = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append({'q': m.question[:80], 'yes': opp.yes_price, 'no': opp.no_price,
                             'sum': opp.total_cost, 'edge': opp.net_edge,
                             'shares': opp.max_shares, 'liq': m.liquidity})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            priced += 1
            if best is None or total < best[0]:
                best = (total, m.question[:60], ya, na, m.liquidity)
            if total <= 1.005:
                near.append((total, m.question[:60], ya, na, m.liquidity))
    near.sort()
    return len(markets), priced, brackets, near, best, scan_time

markets, priced, brackets, near, best, scan_time = asyncio.run(scan())
out = {
    'ts': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()),
    'method': 'min-ask',
    'markets': markets,
    'priced': priced,
    'scan_seconds': scan_time,
    'best_min_sum': best[0] if best else None,
    'brackets': brackets,
    'near_le_1005': [{'sum': t, 'q': q, 'yes': y, 'no': n, 'liq': l} for t, q, y, n, l in near],
}
with open(f"runs/cron_scan_{out['ts']}.json", 'w') as f:
    json.dump(out, f, indent=1)
print(f"markets={markets} priced={priced} brackets={len(brackets)} near={len(near)} "
      f"best_sum={best[0] if best else None} time={scan_time:.1f}s")
for b in brackets:
    print(f"BRACKET: {b}")
for t, q, y, n, l in near[:5]:
    print(f"  {t:.3f} | Yes@{y:.3f} No@{n:.3f} | liq={l} | {q}")
