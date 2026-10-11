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
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    detector_opps = 0
    executions = 0
    two_sided = 0
    yes_only = 0
    no_only = 0
    both_empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        yb_has = bool(yb and yb.asks)
        nb_has = bool(nb and nb.asks)
        if yb_has and nb_has:
            two_sided += 1
        elif yb_has and not nb_has:
            yes_only += 1
        elif nb_has and not yb_has:
            no_only += 1
        else:
            both_empty += 1
        if not (yb_has and nb_has):
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
    return len(markets), priced, rows, detector_opps, executions, (two_sided, yes_only, no_only, both_empty)

markets_n, priced_n, rows, detector_opps, executions, (two_sided, yes_only, no_only, both_empty) = asyncio.run(supp())
print(f"priced markets: {priced_n}/{markets_n}")
if rows:
    print(f"TRUE FLOOR (min-ask sum): {rows[0][0]:.4f} | {rows[0][1]} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]}")
brackets = [r for r in rows if r[0] < 1.0]
band = [r for r in rows if r[0] <= 1.005]
print(f"true brackets (sum<1.00): {len(brackets)}")
for r in brackets:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f}")
print(f"band <=1.005: {len(band)}")
for r in band[:10]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]}")
print("next tier (>1.005):")
for r in rows[len(band):len(band)+6]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]}")
print(f"structural: two_sided {two_sided}, yes_only {yes_only}, no_only {no_only}, both_empty {both_empty}")
print(f"detector-opps: {detector_opps} | paper executions: {executions}")
with open('_tmp_cron_20261011T103107Z_supp_data.json', 'w') as f:
    json.dump({'markets': markets_n, 'priced': priced_n,
               'floor': rows[0][0] if rows else None,
               'floor_q': rows[0][1] if rows else None,
               'floor_yes': rows[0][2] if rows else None,
               'floor_no': rows[0][3] if rows else None,
               'floor_liq': rows[0][4] if rows else None,
               'brackets': len(brackets),
               'band': [list(r) for r in band],
               'structural': {'two_sided': two_sided, 'yes_only': yes_only, 'no_only': no_only, 'both_empty': both_empty},
               'detector_opps': detector_opps,
               'executions': executions}, f)
