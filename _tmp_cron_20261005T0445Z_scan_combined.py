import asyncio, json, logging, time
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
    near_misses = []
    # supplementary: min-ask based near-misses (correct best-ask given DESC-sorted asks)
    near_misses_min = []
    floor_min = None
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
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

                ym = min(yes_book.asks, key=lambda a: float(a['price']))
                nm = min(no_book.asks, key=lambda a: float(a['price']))
                ymp = float(ym['price'])
                nmp = float(nm['price'])
                tm = ymp + nmp
                if m.liquidity > 0 and ymp > 0 and nmp > 0 and ymp < 1.0 and nmp < 1.0:
                    if floor_min is None or tm < floor_min[0]:
                        floor_min = (tm, m.question[:50], ymp, nmp, m.liquidity)
                    if tm <= 1.005:
                        near_misses_min.append((tm, m.question[:50], ymp, nmp, m.liquidity))

    near_misses.sort()
    near_misses_min.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'near_misses_min': near_misses_min,
        'floor_min': floor_min,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"SCANmarkets={result['markets']} scan_time={result['scan_time']:.1f}s")
print(f"BRACKETS={len(result['opps'])}")
for o in result['opps']:
    print(f"  {o['sum']:.3f} edge={o['edge']:.4f} yes@{o['yes']:.3f} no@{o['no']:.3f} shares={o['shares']} liq={o['liq']} | {o['q']}")
print(f"NEARVERBATIM(asks0)={len(result['near_misses'])}")
for t, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {t:.3f} yes@{yp:.3f} no@{np:.3f} liq={liq} | {q}")
print(f"NEARMIN(<=1.005)={len(result['near_misses_min'])}")
for t, q, yp, np, liq in result['near_misses_min'][:10]:
    print(f"  {t:.4f} yes@{yp:.3f} no@{np:.3f} liq={liq} | {q}")
if result['floor_min']:
    t, q, yp, np, liq = result['floor_min']
    print(f"FLOOR min-ask sum={t:.4f} yes@{yp:.3f} no@{np:.3f} liq={liq} | {q}")
with open('_tmp_cron_20261005T0445Z_scan_data.json', 'w') as f:
    json.dump(result, f, default=str)
