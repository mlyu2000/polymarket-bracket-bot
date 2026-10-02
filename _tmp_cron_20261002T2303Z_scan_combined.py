import asyncio, logging, time
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

    # Verbatim-script near-misses use asks[0] (worst ask, DESC order) -> always ~1.0.
    # Corrected near-misses use min(best ask) on both sides.
    opps = []
    near_verbatim = []
    near_min = []
    min_sum = None
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
            paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes0 = float(yes_book.asks[0]['price'])
                no0 = float(no_book.asks[0]['price'])
                t0sum = yes0 + no0
                if t0sum <= 1.005:
                    near_verbatim.append((t0sum, m.question[:50], yes0, no0, m.liquidity))
                ym = min(float(a['price']) for a in yes_book.asks)
                nm = min(float(a['price']) for a in no_book.asks)
                tm = ym + nm
                if min_sum is None or tm < min_sum[0]:
                    min_sum = (tm, m.question[:60], ym, nm, m.liquidity)
                if tm <= 1.005:
                    near_min.append((tm, m.question[:50], ym, nm, m.liquidity))

    near_verbatim.sort()
    near_min.sort()
    return {'markets': len(markets), 'opps': opps,
            'near_verbatim': near_verbatim, 'near_min': near_min,
            'min_sum': min_sum, 'scan_time': scan_time}

r = asyncio.run(scan())
print(f"Scan: {r['markets']} markets in {r['scan_time']:.1f}s")
print(f"BRACKETS (detector, sum<1.00 net-edge gated): {len(r['opps'])}")
for o in r['opps']:
    print(f"  {o['sum']:.4f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']}sh liq={o['liq']:.0f} | {o['q']}")
print(f"Absolute floor (min best asks): {r['min_sum'][0]:.4f} | Yes@{r['min_sum'][2]:.3f} No@{r['min_sum'][3]:.3f} | liq={r['min_sum'][4]:.0f} | {r['min_sum'][1]}")
print(f"Near-miss min-ask <=1.005: {len(r['near_min'])}")
for t, q, yp, np, liq in r['near_min'][:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
