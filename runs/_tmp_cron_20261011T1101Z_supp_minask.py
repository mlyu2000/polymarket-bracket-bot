import asyncio, logging, json, statistics
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
    detector_opps = 0
    executions = 0
    two_sided = yes_only = no_only = both_empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        yask = bool(yb and yb.asks)
        nask = bool(nb and nb.asks)
        if yask and nask:
            two_sided += 1
        elif yask:
            yes_only += 1
        elif nask:
            no_only += 1
        else:
            both_empty += 1
        if not (yask and nask):
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
    return len(markets), priced, rows, detector_opps, executions, two_sided, yes_only, no_only, both_empty

markets_n, priced_n, rows, detector_opps, executions, two_sided, yes_only, no_only, both_empty = asyncio.run(supp())
print(f"priced markets: {priced_n}/{markets_n}")
print(f"two_sided {two_sided} | yes_only {yes_only} | no_only {no_only} | both_empty {both_empty} | not_bracketable {100*(markets_n-two_sided)/markets_n:.1f}%")
if rows:
    print(f"TRUE FLOOR (min-ask sum): {rows[0][0]:.4f} | {rows[0][1]} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]}")
    med = statistics.median(r[0] for r in rows)
    print(f"floor_median: {med:.4f}")
    actionable = [r for r in rows if r[0] < 0.98]
    print(f"actionable (<0.98): {len(actionable)} | floor distance above 0.98: {rows[0][0]-0.98:.4f}")
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
print(f"detector-opps: {detector_opps} | paper executions: {executions}")
with open('/home/ml/projects/polymarket-bracket-bot/runs/_tmp_cron_20261011T1101Z_supp_data.json', 'w') as f:
    json.dump({'markets': markets_n, 'priced': priced_n,
               'two_sided': two_sided, 'yes_only': yes_only, 'no_only': no_only, 'both_empty': both_empty,
               'floor': rows[0][0] if rows else None,
               'floor_q': rows[0][1] if rows else None,
               'floor_median': statistics.median(r[0] for r in rows) if rows else None,
               'brackets': len(brackets),
               'band': [list(r) for r in band],
               'detector_opps': detector_opps,
               'executions': executions}, f)
