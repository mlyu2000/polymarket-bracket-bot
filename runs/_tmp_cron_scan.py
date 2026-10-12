import asyncio, logging, time, json, os, datetime
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    # CLOB /book asks may arrive DESC-sorted; resolve by price, never index 0
    if not book or not book.asks:
        return None
    return min(book.asks, key=lambda a: float(a["price"]))

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
    paper_lines = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'slug': m.slug,
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity,
            })
            paper_result = paper.execute(opp)
            paper_lines.extend(paper_result.log_lines)
            paper_lines.append(f"  -> pnl=${paper_result.final_pnl:.2f} unhedged={paper_result.unhedged}")
        else:
            ya, na = best_ask(yes_book), best_ask(no_book)
            if ya and na:
                yes_price = float(ya["price"])
                no_price = float(na["price"])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity, m.slug))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'paper_lines': paper_lines,
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
for line in result['paper_lines']:
    print(f"  {line}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq, slug in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq ${liq:,.0f} | {q}")

ts = datetime.datetime.now(datetime.timezone.utc)
os.makedirs('runs', exist_ok=True)
supp = {
    'ts': ts.isoformat(),
    'markets': result['markets'],
    'scan_time_s': round(result['scan_time'], 1),
    'opps': result['opps'],
    'near_misses': [
        {'total': t, 'q': q, 'yes': yp, 'no': np, 'liq': liq, 'slug': slug}
        for t, q, yp, np, liq, slug in result['near_misses']
    ],
}
out = f"runs/_tmp_cron_{ts.strftime('%Y%m%dT%H%M%SZ')}_supp_data.json"
with open(out, 'w') as f:
    json.dump(supp, f, indent=2)
print(f"💾 Supp data: {out}")
