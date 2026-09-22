import asyncio, logging, time, json, datetime
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    scan_seconds = time.time() - t0

    brackets = []
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append({
                'q': m.question[:80], 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity,
            })
            paper.execute(opp)
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            rows.append((ya + na, m.question[:80], ya, na, m.liquidity))
    rows.sort()
    near = [list(r) for r in rows if 1.0 <= r[0] <= 1.005]
    sub1 = [list(r) for r in rows if r[0] < 1.0]

    print(f"min-ask supplement over {priced}/{len(markets)} priced markets")
    print("top-8 floors:")
    for t, q, ya, na, liq in rows[:8]:
        flag = ' <<< SUM<1.00' if t < 1.0 else ''
        print(f"  {t:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq:,.0f} | {q}{flag}")
    print(f"min-ask sum<1.00 count: {len(sub1)}")
    print(f"min-ask near-miss (1.000-1.005) count: {len(near)}")

    out = {
        'ts': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'markets': len(markets),
        'priced': priced,
        'scan_seconds': round(scan_seconds, 1),
        'method': 'min-ask',
        'brackets': brackets,
        'near_le_1005': near,
    }
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    path = f'runs/cron_scan_{ts}.json'
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print(f'saved {path}: {len(brackets)} brackets, {len(near)} near-misses')

asyncio.run(main())
