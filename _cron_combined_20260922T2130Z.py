import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []   # provided script basis: asks[0] (raw; DESC-sorted CLOB asks => worst ask)
    minask = []        # corrected basis: min-ask floor, same as detector.py
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity
            })
            paper_result = paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                priced += 1
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))
                cy = min(float(a['price']) for a in yes_book.asks)
                cn = min(float(a['price']) for a in no_book.asks)
                minask.append({
                    'sum': round(cy + cn, 6), 'q': m.question[:60],
                    'yes': cy, 'no': cn, 'liq': m.liquidity
                })

    near_misses.sort()
    minask.sort(key=lambda d: d['sum'])
    near_le = [d for d in minask if d['sum'] <= 1.005]
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    record = {
        'ts': ts,
        'method': 'provided(asks[0]) + detector + minask floor',
        'markets': len(markets),
        'priced': priced,
        'scan_seconds': round(scan_time, 2),
        'best_min_sum': minask[0]['sum'] if minask else None,
        'brackets': opps,
        'near_le_1005_provided_asks0': near_misses,
        'near_le_1005_minask': near_le,
    }
    path = f'runs/cron_scan_{ts}.json'
    with open(path, 'w') as f:
        json.dump(record, f, indent=1)
    print(f"WROTE {path}")
    print(f"markets={len(markets)} priced={priced} brackets={len(opps)} "
          f"floor={record['best_min_sum']} le1005={len(near_le)} asks0_near={len(near_misses)}")
    print("--- DETECTOR BRACKETS:", len(opps))
    for o in opps:
        print(f"  sum={o['sum']:.3f} edge={o['edge']:.4f} Y@{o['yes']:.3f} N@{o['no']:.3f} sh={o['shares']} liq={o['liq']} | {o['q']}")
    print("--- PROVIDED (asks[0]) NEAR-MISS <=1.005:", len(near_misses))
    for total, q, yp, np_, liq in near_misses[:5]:
        print(f"  {total:.3f} | Y@{yp:.3f} N@{np_:.3f} | {q}")
    print("--- MIN-ASK FLOOR (detector basis): best 5 sums")
    for d in minask[:5]:
        print(f"  {d['sum']:.3f} | Y@{d['yes']:.3f} N@{d['no']:.3f} | liq={d['liq']} | {d['q']}")
    print(f"--- MIN-ASK NEAR-MISS <=1.005: {len(near_le)}")
    for d in near_le[:10]:
        print(f"  {d['sum']:.3f} | Y@{d['yes']:.3f} N@{d['no']:.3f} | liq={d['liq']} | {d['q']}")

result = asyncio.run(scan())
