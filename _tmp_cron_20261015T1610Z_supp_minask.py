"""Supplementary min-ask diagnostic — source of truth.
CLOB /book asks are DESC-sorted; asks[0] is the WORST ask, so the verbatim
near-miss block (which uses asks[0]) always reports 0. Compute min over ALL asks.
"""
import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    results = []   # markets with two-sided books
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        try:
            min_yes = min(float(a['price']) for a in yes_book.asks)
            min_no = min(float(a['price']) for a in no_book.asks)
        except (KeyError, ValueError, TypeError):
            continue
        results.append({
            'q': m.question,
            'min_yes': min_yes,
            'min_no': min_no,
            'total': min_yes + min_no,
            'liq': m.liquidity,
        })

    results.sort(key=lambda r: r['total'])

    print(f"🔍 Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"Two-sided books: {len(results)}")

    brackets = [r for r in results if r['total'] < 1.00]
    print(f"✅ BRACKETS (min-ask sum < 1.00): {len(brackets)}")
    for r in brackets:
        print(f"  🔴 {r['total']:.4f} | Yes@{r['min_yes']:.4f} No@{r['min_no']:.4f} | liq={r['liq']} | {r['q'][:70]}")

    print("📊 TOP-25 nearest min-ask sums:")
    for r in results[:25]:
        print(f"  {r['total']:.4f} | Yes@{r['min_yes']:.4f} No@{r['min_no']:.4f} | liq={r['liq']:>10.1f} | {r['q'][:70]}")

    tiers = {
        'le1.005': sum(1 for r in results if r['total'] <= 1.005),
        'le1.010': sum(1 for r in results if r['total'] <= 1.010),
        'le1.020': sum(1 for r in results if r['total'] <= 1.020),
        'le1.050': sum(1 for r in results if r['total'] <= 1.050),
        'lt1.000': sum(1 for r in results if r['total'] < 1.000),
    }
    print(f"tiers: {json.dumps(tiers)}")

    with open('runs/_tmp_cron_20261015T1610Z_supp_data.json', 'w') as f:
        json.dump({
            'scan_time': scan_time,
            'markets': len(markets),
            'two_sided': len(results),
            'brackets': brackets,
            'top25': results[:25],
            'tiers': tiers,
        }, f, indent=2, default=str)
    print("saved: runs/_tmp_cron_20261015T1610Z_supp_data.json")

result = asyncio.run(scan())
