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
    priced = 0
    yes_only = 0
    no_only = 0
    both_empty = 0
    detector_opps = 0
    executions = 0
    for m, (yb, nb) in zip(markets, all_books):
        has_y = bool(yb and yb.asks)
        has_n = bool(nb and nb.asks)
        if has_y and has_n:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
            opp = detector.detect(m, yb, nb)
            if opp:
                detector_opps += 1
                executions += 1 if paper.execute(opp) else 0
        elif has_y:
            yes_only += 1
        elif has_n:
            no_only += 1
        else:
            both_empty += 1
    rows.sort()
    med = rows[len(rows)//2][0] if rows else None
    return (len(markets), priced, yes_only, no_only, both_empty, rows,
            med, detector_opps, executions)

(markets_n, priced_n, yes_only, no_only, both_empty, rows, med,
 detector_opps, executions) = asyncio.run(supp())

print(f"priced: {priced_n}/{markets_n} | yes-only: {yes_only} | no-only: {no_only} | both-empty: {both_empty}")
print(f"median min-ask sum: {med:.4f}" if med else "median: n/a")
if rows:
    print(f"TRUE FLOOR (min-ask sum): {rows[0][0]:.4f} | {rows[0][1]} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]:.2f}")
brackets = [r for r in rows if r[0] < 1.0]
band = [r for r in rows if r[0] <= 1.005]
print(f"true brackets (sum<1.00): {len(brackets)}")
for r in brackets:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
print(f"band <=1.005: {len(band)}")
for r in band[:12]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
print("next tier (>1.005):")
for r in rows[len(band):len(band)+6]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
print(f"detector-opps: {detector_opps} | paper executions: {executions}")
with open('_cron_20261011T1215Z_supp_data.json', 'w') as f:
    json.dump({'markets': markets_n, 'priced': priced_n,
               'yes_only': yes_only, 'no_only': no_only, 'both_empty': both_empty,
               'median': med,
               'floor': rows[0][0] if rows else None,
               'floor_q': rows[0][1] if rows else None,
               'brackets': len(brackets),
               'band': [list(r) for r in band],
               'detector_opps': detector_opps,
               'executions': executions}, f)
