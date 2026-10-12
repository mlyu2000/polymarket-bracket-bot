import asyncio, logging, time, json
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
    minask_rows = []
    priced = 0
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

        # authoritative min-ask measurement (asks are DESC-sorted on CLOB)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            minask_rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
            priced += 1

    near_misses.sort()
    minask_rows.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'priced': priced,
        'minask_rows': minask_rows,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

print()
print("=== SUPPLEMENT (authoritative min-ask) ===")
rows = result['minask_rows']
brackets_true = [r for r in rows if r[0] < 1.0]
print(f"priced markets: {result['priced']}")
print(f"TRUE brackets (min-ask sum < 1.0): {len(brackets_true)}")
for r in brackets_true[:10]:
    print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
print("top 5 best sums (min-ask):")
for r in rows[:5]:
    print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")

band = [list(r) for r in rows if r[0] <= 1.005]
data = {
    'markets': result['markets'],
    'scan_time': result['scan_time'],
    'priced': result['priced'],
    'floor': (rows[0][0] if rows else None),
    'band': band,
    'top20': [list(r) for r in rows[:20]],
    'opps_verbatim': result['opps'],
    'near_misses_verbatim': [list(x) for x in result['near_misses']],
}
with open('_tmp_cron_20261010T1205Z_data.json', 'w') as f:
    json.dump(data, f)
print("saved: _tmp_cron_20261010T1205Z_data.json")
