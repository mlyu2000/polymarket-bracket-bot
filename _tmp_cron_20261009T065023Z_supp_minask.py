import asyncio, logging, time, json
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
    priced = 0
    detector_hits = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            detector_hits += 1
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        # True best ask = min over ladder (CLOB /book returns asks DESC-sorted,
        # so asks[0] is the WORST ask ~0.999)
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        rows.append({'sum': round(total, 5), 'yes': yp, 'no': np_,
                     'q': m.question[:70], 'liq': m.liquidity})
    rows.sort(key=lambda r: r['sum'])
    return {'markets': len(markets), 'priced': priced,
            'detector_hits': detector_hits, 'rows': rows}

res = asyncio.run(scan())
print(f"min-ask pass: {res['markets']} markets, {res['priced']} priced both-sides, detector_hits={res['detector_hits']}")
print("TRUE floor (10 lowest Yes+No best-ask sums):")
for r in res['rows'][:10]:
    print(f"  {r['sum']:.4f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")
brackets = [r for r in res['rows'] if r['sum'] < 1.0]
near = [r for r in res['rows'] if 1.0 <= r['sum'] <= 1.005]
print(f"true brackets (<1.00): {len(brackets)} | true near (1.000-1.005): {len(near)}")
with open('/home/ml/projects/polymarket-bracket-bot/_tmp_cron_20261009T0640Z_supp_data.json', 'w') as f:
    json.dump(res, f)
