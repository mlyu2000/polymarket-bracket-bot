# Supplementary: near-miss floor using BEST asks (min price), not asks[0].
# Polymarket CLOB /book lists asks DESC-sorted, so asks[0] is the worst ask;
# detector.py correctly uses min(). This mirrors the detector for near-misses.
import asyncio, logging, json, time
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
    elapsed = time.time() - t0

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        if m.liquidity is not None and m.liquidity <= 0:
            continue
        try:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
        except (KeyError, TypeError, ValueError):
            continue
        priced += 1
        rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))

    rows.sort()
    print(f"minask scan: {len(markets)} markets, {priced} both-sides-priced, {elapsed:.1f}s")
    if rows:
        print(f"TRUE FLOOR (min best-ask sum): {rows[0][0]:.4f}")
    br = [r for r in rows if r[0] < 1.0]
    print(f"best-ask brackets (<1.00): {len(br)}")
    for r in br[:10]:
        print(f"  🔴 {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    print("bottom-10 best-ask sums:")
    for r in rows[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses (best-ask sum <= 1.005): {len(nm)}")

    # Persist run record (git-persisted runs/ dir per user mandate)
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    band = [r for r in rows if r[0] <= 1.005]
    out = {
        'run': ts,
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'markets': len(markets),
        'priced': priced,
        'floor': round(rows[0][0], 4) if rows else None,
        'brackets_minask': len(br),
        'band': len(band),
        'top8': [{'sum': round(r[0],4), 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]} for r in rows[:8]],
        'scan_time_s': round(elapsed, 1),
    }
    with open(f'runs/scan_{ts}.json', 'w') as f:
        json.dump(out, f, indent=1)
    print(f"persisted -> runs/scan_{ts}.json")

asyncio.run(scan())
