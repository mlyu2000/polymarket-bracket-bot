import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    cheapest = []
    priced = 0
    yes_only = 0
    no_only = 0
    both_empty = 0
    detector_opps = 0
    executions = 0
    for m, (yb, nb) in zip(markets, all_books):
        y_asks = bool(yb and yb.asks)
        n_asks = bool(nb and nb.asks)
        if y_asks and n_asks:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            wy = max(float(a['price']) for a in yb.asks)
            wn = max(float(a['price']) for a in nb.asks)
            rows.append((round(yp + np_, 4), m.question[:60], yp, np_, m.liquidity))
            cheapest.append({'total': round(yp + np_, 4), 'yes': yp, 'no': np_,
                             'worst_yes': wy, 'worst_no': wn, 'liq': m.liquidity,
                             'q': m.question[:60]})
        elif y_asks and not n_asks:
            yes_only += 1
        elif n_asks and not y_asks:
            no_only += 1
        else:
            both_empty += 1
        opp = detector.detect(m, yb, nb)
        if opp:
            detector_opps += 1
            if paper.execute(opp):
                executions += 1
    rows.sort()
    cheapest.sort(key=lambda d: d['total'])
    return len(markets), priced, yes_only, no_only, both_empty, rows, detector_opps, executions, cheapest

markets_n, priced_n, yes_only, no_only, both_empty, rows, detector_opps, executions, cheapest = asyncio.run(supp())
print(f"priced markets (both-side asks): {priced_n}/{markets_n}")
print(f"book sides: yes_only={yes_only} no_only={no_only} both_empty={both_empty} -> not bracket-able via asks: {markets_n - priced_n} ({(markets_n - priced_n)/markets_n*100:.1f}%)")
if rows:
    print(f"TRUE FLOOR (min-ask sum): {rows[0][0]:.4f} | {rows[0][1]} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]:.2f}")
brackets = [r for r in rows if r[0] < 1.0]
band = [r for r in rows if r[0] <= 1.005]
print(f"true brackets (sum<1.00): {len(brackets)}")
for r in brackets:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f}")
print(f"band <=1.005: {len(band)}")
for r in band[:8]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
print("next tier (>1.005):")
for r in rows[len(band):len(band)+6]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
import statistics
med = statistics.median([r[0] for r in rows]) if rows else None
print(f"median priced floor: {med:.4f}" if med else "median: n/a")
print(f"detector-opps: {detector_opps} | paper executions: {executions}")
with open('runs/_tmp_cron_20261011T141532Z_minask_supp.json', 'w') as f:
    json.dump({'ts': '2026-10-11T14:15:32Z', 'markets': markets_n,
               'books': {'two_sided': priced_n, 'yes_only': yes_only,
                         'no_only': no_only, 'none': both_empty},
               'floor': rows[0][0] if rows else None,
               'floor_q': rows[0][1] if rows else None,
               'median_floor': med,
               'brackets': [list(r) for r in brackets],
               'band_1005': len(band),
               'cheapest_12': cheapest[:12],
               'detector_opps': detector_opps, 'executions': executions}, f, indent=1)
print("persisted: runs/_tmp_cron_20261011T141532Z_minask_supp.json")
