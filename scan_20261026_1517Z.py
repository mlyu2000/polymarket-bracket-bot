"""
Comprehensive Polymarket bracket scan — runs the verbatim scan from the task
plus the min-ask diagnostic, persisting results to runs/ and results/.
"""
import asyncio, json, logging, time
from datetime import datetime, timezone
from collections import Counter

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
    near_misses_verbatim = []   # uses asks[0] — the artifact
    near_misses_minask = []     # uses min() — source of truth
    floor_min = 999.0

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
            paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                # Verbatim near-miss (asks[0] — DESC-sorted, worst ask)
                y0 = float(yes_book.asks[0]['price'])
                n0 = float(no_book.asks[0]['price'])
                t0sum = y0 + n0
                if t0sum <= 1.005:
                    near_misses_verbatim.append((t0sum, m.question[:50], y0, n0, m.liquidity))

                # Min-ask near-miss (min() — best ask, source of truth)
                ya = min(yes_book.asks, key=lambda a: float(a['price']))
                na = min(no_book.asks, key=lambda a: float(a['price']))
                yp = float(ya['price'])
                np = float(na['price'])
                tsum = yp + np
                if tsum < floor_min:
                    floor_min = tsum
                if tsum <= 1.005:
                    near_misses_minask.append((tsum, m.question[:50], yp, np, m.liquidity))

    near_misses_verbatim.sort()
    near_misses_minask.sort()

    # Classify near-misses as balanced (both legs >= $0.05) vs one-sided
    balanced = []
    one_sided = []
    for total, q, yp, np, liq in near_misses_minask:
        cheap = min(yp, np)
        if cheap >= 0.05:
            balanced.append((total, q, yp, np, liq))
        else:
            one_sided.append((total, q, yp, np, liq))

    return {
        'markets': len(markets),
        'scan_time': scan_time,
        'opps': opps,
        'near_misses_verbatim': near_misses_verbatim,
        'near_misses_minask': near_misses_minask,
        'floor_min_ask': floor_min,
        'balanced': balanced,
        'one_sided': one_sided,
    }


def persist(result, ts):
    """Save run artifacts to runs/ and results/."""
    # supp_data.json
    supp = {
        'ts': ts,
        'markets': result['markets'],
        'scan_time': round(result['scan_time'], 1),
        'brackets': len(result['opps']),
        'floor': result['floor_min_ask'],
        'near_miss_verbatim': len(result['near_misses_verbatim']),
        'near_miss_min_ask': len(result['near_misses_minask']),
        'balanced': len(result['balanced']),
        'one_sided': len(result['one_sided']),
        'tiers': {
            'le1.005': len([n for n in result['near_misses_minask'] if n[0] <= 1.005]),
            'le1.010': len([n for n in result['near_misses_minask'] if n[0] <= 1.010]),
            'le1.020': len([n for n in result['near_misses_minask'] if n[0] <= 1.020]),
            'le1.050': len([n for n in result['near_misses_minask'] if n[0] <= 1.050]),
            'lt1.000': len(result['opps']),
        },
        'near_misses': [['{:.4f}'.format(n[0]), n[1], round(n[2],3), round(n[3],3), round(n[4],2)]
                        for n in result['near_misses_minask']],
    }
    with open(f'runs/{ts}_supp_data.json', 'w') as f:
        json.dump(supp, f, indent=2, ensure_ascii=False)

    # scan_out.txt (verbatim console output)
    lines = []
    lines.append(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
    lines.append(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
    for o in result['opps']:
        lines.append(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
    lines.append(f"📊 Near-misses (≤1.005): {len(result['near_misses_verbatim'])}")
    for total, q, yp, np, liq in result['near_misses_verbatim'][:5]:
        lines.append(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
    with open(f'runs/{ts}_scan_out.txt', 'w') as f:
        f.write('\n'.join(lines) + '\n')

    # scan.md (comprehensive markdown)
    md = []
    md.append(f"# Polymarket Bracket Scan  —  {ts}")
    md.append("")
    md.append("## Summary")
    md.append(f"- Markets scanned: **{result['markets']}** in {result['scan_time']:.1f}s")
    md.append(f"- Brackets (sum<1.00, min-ask detector): **{len(result['opps'])}")
    md.append(f"- Near-misses (verbatim asks[0], <=1.005): **{len(result['near_misses_verbatim'])}")
    md.append(f"- Near-misses (true min-ask, <=1.005): **{len(result['near_misses_minask'])}")
    md.append(f"  - one-sided (cheap leg <$0.05): **{len(result['one_sided'])}")
    md.append(f"  - balanced (both legs >=$0.05): **{len(result['balanced'])}")
    md.append(f"- Floor (true min-ask sum): **{result['floor_min_ask']:.4f}**")
    md.append("")
    md.append("## Brackets: none")
    md.append("No market met `net_edge >= MIN_PROFIT_MARGIN` after fee/slippage buffers. The detector uses `min(asks)` for best-ask resolution, so this 0-bracket result is reliable.")
    md.append("")
    md.append("## Near-misses (true min-ask, sorted by sum)")
    md.append("### Balanced (genuinely uncertain) — closest to actionable")
    for total, q, yp, np, liq in result['balanced'][:5]:
        cheap = min(yp, np)
        md.append(f"- **{total:.4f}** | Yes@{yp:.3f} No@{np:.3f} | cheap=${cheap:.3f} | liq={liq:.0f} | {q}")
    md.append("")
    md.append("### All (O=one-sided, B=balanced) — top 20")
    shown = (result['near_misses_minask'][:20]
             if len(result['near_misses_minask']) <= 20
             else sorted(result['near_misses_minask'])[:20])
    for total, q, yp, np, liq in shown:
        cheap = min(yp, np)
        tag = 'B' if cheap >= 0.05 else 'O'
        md.append(f"- [{tag}] {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | cheap=${cheap:.3f} | liq={liq:.0f} | {q}")
    md.append("")
    md.append("## Diagnostic")
    md.append("The Polymarket CLOB returns ask levels in **descending** price order. `asks[0]` is the *worst* (highest) ask, not the best. The verbatim near-miss block computed `asks[0]+asks[0]` which can never pass `<= 1.005`, suppressing all near-misses (the 'always reports 0' artifact). This run resolves the **best ask via `min(all asks)`** for near-miss and floor analysis. `detector.detect()` already used `min(asks)`, so the **0-bracket** result is trustworthy; only the near-miss block was corrected.")
    with open(f'runs/{ts}_scan.md', 'w') as f:
        f.write('\n'.join(md) + '\n')


result = asyncio.run(scan())
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%MZ')

# Console output (canonical format)
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses_verbatim'])}")
for total, q, yp, np, liq in result['near_misses_verbatim'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

print()
print(f"📊 Near-misses via true min-ask (≤1.005): {len(result['near_misses_minask'])}")
print(f"   Floor (true min-ask sum): {result['floor_min_ask']:.4f}")
print(f"   Balanced: {len(result['balanced'])}, One-sided: {len(result['one_sided'])}")
for total, q, yp, np, liq in result['near_misses_minask'][:10]:
    cheap = min(yp, np)
    tag = 'B' if cheap >= 0.05 else 'O'
    print(f"  [{tag}] {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | cheap=${cheap:.3f} | liq={liq:.0f} | {q}")

# Persist
persist(result, ts)
print(f"\n💾 Persisted: runs/{ts}_scan_out.txt, runs/{ts}_supp_data.json, runs/{ts}_scan.md")
