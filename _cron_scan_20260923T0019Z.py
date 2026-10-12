import asyncio, logging, time, json, os
from datetime import datetime, timezone
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

    def best_ask(book):
        # CLOB asks are DESC-sorted; asks[0] is the WORST ask. min() = true floor.
        if not book or not getattr(book, 'asks', None):
            return None
        return float(min(book.asks, key=lambda a: float(a['price']))['price'])

    opps = []
    near_misses = []
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

    near_misses.sort()

    # --- min-ask verification pass (house convention, detector-consistent) ---
    verified_opps = []
    all_sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        ya, na = best_ask(yes_book), best_ask(no_book)
        if ya is None or na is None:
            continue
        s = ya + na
        all_sums.append((s, m.question[:50]))
        if s < 1.0:
            verified_opps.append({'q': m.question[:60], 'yes': ya, 'no': na, 'sum': s, 'liq': m.liquidity})
    verified_opps.sort(key=lambda o: o['sum'])
    all_sums.sort()
    floor = all_sums[0] if all_sums else None
    minask_near = [t for t in all_sums if t[0] <= 1.005]

    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'verified_opps': verified_opps,
        'floor': floor,
        'minask_near': minask_near,
        'priced': len(all_sums),
    }

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
print(f"🔎 MIN-ASK VERIFICATION (detector-consistent floor):")
if result['floor']:
    print(f"  priced markets: {result['priced']} | true floor: {result['floor'][0]:.3f} ({result['floor'][1]})")
else:
    print("  no priced markets")
print(f"  brackets (min-ask sum < 1.00): {len(result['verified_opps'])}")
for o in result['verified_opps'][:10]:
    print(f"  🟢 {o['sum']:.4f} | Yes@{o['yes']:.3f} No@{o['no']:.3f} | liq={o['liq']} | {o['q']}")
print(f"  min-ask near-misses (≤1.005): {len(result['minask_near'])}")
for total, q in result['minask_near'][:8]:
    print(f"  {total:.4f} | {q}")

# persist run
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out = {
    'ts': ts,
    'markets': result['markets'],
    'priced': result['priced'],
    'scan_time': result['scan_time'],
    'opps': result['opps'],
    'near_misses': result['near_misses'][:20],
    'verified_opps': result['verified_opps'],
    'floor': result['floor'],
    'minask_near': [list(t) for t in result['minask_near'][:30]],
}
os.makedirs('runs', exist_ok=True)
path = f'runs/scan_{ts}.json'
with open(path, 'w') as f:
    json.dump(out, f, indent=2)
print(f"💾 saved {path}")
