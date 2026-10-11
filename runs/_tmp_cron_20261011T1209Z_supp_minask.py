import asyncio, logging, json, statistics
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
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    two_sided = yes_only = no_only = both_empty = 0
    detector_opps = 0
    executions = 0
    for m, (yb, nb) in zip(markets, all_books):
        y_asks = bool(yb and yb.asks)
        n_asks = bool(nb and nb.asks)
        if y_asks and n_asks:
            two_sided += 1
            yp = min(float(a['price']) for a in yb.asks)
        elif y_asks:
            yes_only += 1
            yp = None
        elif n_asks:
            no_only += 1
            yp = None
        else:
            both_empty += 1
            yp = None
        if yp is not None:
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
        opp = detector.detect(m, yb, nb)
        if opp:
            detector_opps += 1
            executions += 1 if paper.execute(opp) else 0
    rows.sort()
    return len(markets), two_sided, yes_only, no_only, both_empty, rows, detector_opps, executions

markets_n, ts, yo, no, be, rows, detector_opps, executions = asyncio.run(scan())
floors = [r[0] for r in rows]
median = statistics.median(floors) if floors else None
band = [r for r in rows if r[0] <= 1.005]
brackets = [r for r in rows if r[0] < 1.0]
print(f"markets: {markets_n} | two_sided(priced): {ts} | yes_only: {yo} | no_only: {no} | both_empty: {be}")
print(f"TRUE FLOOR: {rows[0][0]:.4f} | {rows[0][1]} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]:.2f}")
print(f"median floor: {median:.4f}")
print(f"brackets (<1.00): {len(brackets)} | band<=1.005: {len(band)}")
for r in band:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
print("next tier:")
for r in rows[len(band):len(band)+4]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.2f}")
print(f"detector-opps: {detector_opps} | paper executions: {executions}")
data = {
    'ts': '20261011T1209Z',
    'markets': markets_n,
    'brackets': len(brackets),
    'paper_executions': executions,
    'book_shape': {'two_sided': ts, 'one_sided_yes_only': yo, 'one_sided_no_only': no, 'both_empty': be},
    'true_floor': {
        'min': rows[0][0] if rows else None,
        'median': median,
        'actionable_below_0.98': len([r for r in rows if r[0] < 0.98]),
        'best_gross_edge': (1.0 - rows[0][0]) if rows else None,
        'gap_to_actionable_threshold': (rows[0][0] - 0.98) if rows else None,
        'band_le_1.005': len(band),
        'top': [{'floor': r[0], 'yes': r[2], 'no': r[3], 'liq': round(r[4], 2), 'q': r[1]} for r in rows[:10]],
    },
    'detector_opps': detector_opps,
}
with open('runs/_tmp_cron_20261011T1209Z_supp_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print('saved runs/_tmp_cron_20261011T1209Z_supp_data.json')
