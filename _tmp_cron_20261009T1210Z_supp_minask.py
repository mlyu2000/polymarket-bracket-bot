import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    elapsed = time.time() - t0

    rows = []
    det_opps = 0
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            det_opps += 1
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        ya = [float(a['price']) for a in yes_book.asks]
        na = [float(a['price']) for a in no_book.asks]
        yp, np_ = min(ya), min(na)
        total = yp + np_
        if total <= 1.005:
            rows.append({'sum': round(total, 4), 'q': m.question[:70],
                         'yes': yp, 'no': np_, 'liq': m.liquidity})
    rows.sort(key=lambda r: r['sum'])
    return {'markets': len(markets), 'elapsed': elapsed, 'priced': priced,
            'detector_opps': det_opps, 'band': rows}

result = asyncio.run(supp())
print(f"Supp min-ask scan: {result['markets']} markets in {result['elapsed']:.1f}s")
print(f"Detector opportunities: {result['detector_opps']}")
print(f"Min-ask near-misses (sum <= 1.005): {len(result['band'])}")
for r in result['band'][:15]:
    print(f"  {r['sum']:.3f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")

with open('_tmp_cron_20261009T1210Z_supp_data.json', 'w') as f:
    json.dump(result, f, default=str)
