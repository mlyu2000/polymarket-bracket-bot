import asyncio, logging, json, time
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
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0
    rows = []
    priced = 0
    one_sided = 0
    detector_opps = 0
    executions = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            if (yb and yb.asks) != (nb and nb.asks) or (yb and yb.asks):
                one_sided += 1
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
        opp = detector.detect(m, yb, nb)
        if opp:
            detector_opps += 1
            executions += 1 if paper.execute(opp) else 0
    rows.sort()
    return len(markets), priced, one_sided, rows, detector_opps, executions, scan_time

markets_n, priced_n, one_sided_n, rows, detector_opps, executions, scan_time = asyncio.run(supp())
print(f"scan: {markets_n} markets in {scan_time:.1f}s | priced (both-sided): {priced_n} | one-sided: {one_sided_n}")
if rows:
    print(f"TRUE FLOOR (min-ask sum): {rows[0][0]:.4f} | {rows[0][1]} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]}")
brackets = [r for r in rows if r[0] < 1.0]
band = [r for r in rows if r[0] <= 1.005]
print(f"true brackets (sum<1.00): {len(brackets)}")
for r in brackets:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f}")
print(f"band <=1.005: {len(band)}")
for r in band[:8]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]}")
print("next tier (>1.005):")
for r in rows[len(band):len(band)+6]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]}")
if len(rows) > 1:
    print(f"median: {rows[len(rows)//2][0]:.4f}")
print(f"detector-opps: {detector_opps} | paper executions: {executions}")
with open('runs/_tmp_cron_20261011T0239Z_supp_data.json', 'w') as f:
    json.dump({'ts': '20261011T0239Z', 'markets': markets_n, 'priced': priced_n,
               'one_sided': one_sided_n, 'scan_time': scan_time,
               'floor': rows[0][0] if rows else None,
               'floor_q': rows[0][1] if rows else None,
               'brackets': len(brackets),
               'band': [list(r) for r in band],
               'detector_opps': detector_opps,
               'executions': executions}, f, indent=1)
