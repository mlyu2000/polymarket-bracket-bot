import asyncio, json, logging, os, time, datetime
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)


def _min_ask(book):
    """True best ask. asks[] is DESC-sorted, so asks[0] is the WORST ask."""
    if not book or not book.asks:
        return None
    return min(float(a['price']) for a in book.asks)


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
    floor_pairs = []
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
            # NOTE: asks[] is DESC-sorted (asks[0] == worst ask, often ~0.999),
            # so asks[0] understates the floor. Use the true best ask (min).
            yes_price = _min_ask(yes_book)
            no_price = _min_ask(no_book)
            if yes_price is not None and no_price is not None:
                total = yes_price + no_price
                floor_pairs.append(total)
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    floor_pairs.sort()
    tiers = {f"le{t:.3f}": sum(1 for f in floor_pairs if f <= t)
             for t in (1.005, 1.010, 1.020, 1.050)}
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'floor': floor_pairs[0] if floor_pairs else None,
        'two_sided': len(floor_pairs),
        'tiers': tiers,
        'top_floor': [round(f, 3) for f in floor_pairs[:12]],
    }

def _persist(result):
    """Write run artifacts under runs/ (git-persisted)."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%MZ')
    os.makedirs('runs', exist_ok=True)
    lines = [
        f"# Bracket scan {ts}",
        f"markets={result['markets']} scan_time={result['scan_time']:.1f}s",
        f"brackets={len(result['opps'])}",
        f"near_misses_le_1.005={len(result['near_misses'])}",
        f"floor={result['floor']}",
        f"two_sided={result['two_sided']}",
        f"tiers={result['tiers']}",
        "",
    ]
    for o in result['opps']:
        lines.append(
            f"BRACKET {o['sum']:.3f} edge={o['edge']:.4f} "
            f"Yes@{o['yes']:.3f} No@{o['no']:.3f} shares={o['shares']} liq={o['liq']} | {o['q']}")
    for total, q, yp, np_, liq in result['near_misses']:
        lines.append(f"NEARMISS {total:.3f} Yes@{yp:.3f} No@{np_:.3f} liq={liq} | {q}")
    with open(f"runs/{ts}_scan_out.txt", 'w') as fh:
        fh.write("\n".join(lines) + "\n")
    with open(f"runs/{ts}_supp_data.json", 'w') as fh:
        json.dump({
            'ts': ts,
            'markets': result['markets'],
            'brackets': len(result['opps']),
            'floor': result['floor'],
            'two_sided': result['two_sided'],
            'tiers': result['tiers'],
            'band': [[t, q, y, n, l] for t, q, y, n, l in result['near_misses']],
            'priced': result['two_sided'],
        }, fh, indent=2)
    return ts

result = asyncio.run(scan())
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
if result['floor'] is not None:
    print(f"📉 FLOOR (min two-sided min-ask sum): {result['floor']:.3f}")
print(f"🧱 Two-sided pairs: {result['two_sided']}/{result['markets']}")
print("📏 Tiers: " + " | ".join(f"{k} n{v}" for k, v in result['tiers'].items()))
print("🏅 Top-12 tightest: " + ", ".join(f"{f:.3f}" for f in result['top_floor']))
ts = _persist(result)
print(f"💾 Persisted runs/{ts}_scan_out.txt + runs/{ts}_supp_data.json")
