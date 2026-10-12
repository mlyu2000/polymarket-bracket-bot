import asyncio, logging, time, json, collections
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    structural = collections.Counter()
    brackets = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if detector.detect(m, yes_book, no_book):
            brackets += 1
        ya = yes_book.asks if yes_book else None
        na = no_book.asks if no_book else None
        if ya and na:
            structural['two_sided'] += 1
            yp = min(float(a['price']) for a in ya)
            np_ = min(float(a['price']) for a in na)
            rows.append((round(yp + np_, 4), m.question, round(yp, 4), round(np_, 4), round(m.liquidity, 2)))
        elif ya and not na:
            structural['yes_only'] += 1
        elif na and not ya:
            structural['no_only'] += 1
        else:
            structural['empty'] += 1

    rows.sort()
    tiers = {f'le_{t}': sum(1 for r in rows if r[0] <= t / 1000) for t in (1000, 1005, 1010, 1020, 1030)}
    out = {
        'ts': '20261012T114614Z',
        'markets': len(markets),
        'scan_time_s': round(scan_time, 1),
        'brackets': brackets,
        'structural': dict(structural),
        'tiers': tiers,
        'floor': rows[0] if rows else None,
        'lowest_15': rows[:15],
    }
    with open('runs/_tmp_cron_20261012T114614Z_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != 'lowest_15'}, indent=2, default=str))
    for total, q, yp, np_, liq in rows[:15]:
        print(f"  {total:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q[:70]}")

asyncio.run(scan())
