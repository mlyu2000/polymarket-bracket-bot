import asyncio, logging, time, json, datetime
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not book.asks:
        return None
    return min(book.asks, key=lambda a: float(a["price"]))

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        ya, na = best_ask(yb), best_ask(nb)
        yp = float(ya["price"]) if ya else None
        np_ = float(na["price"]) if na else None
        total = (yp + np_) if (yp is not None and np_ is not None) else None
        rows.append({
            'q': m.question, 'slug': m.slug,
            'yes': yp, 'no': np_, 'total': total,
            'liq': m.liquidity, 'active': m.active, 'closed': m.closed,
        })
    return markets, rows

markets, rows = asyncio.run(scan())

totals = [r['total'] for r in rows if r['total'] is not None]
active = [r for r in rows if r['total'] is not None and r['active'] and not r['closed'] and r['liq'] > 0]
at = [r['total'] for r in active]

bands = {'<=1.005': 0, '<=1.010': 0, '<=1.020': 0, '<=1.030': 0, '<=1.050': 0, '<1.000': 0}
for t in at:
    if t < 1.000: bands['<1.000'] += 1
    if t <= 1.005: bands['<=1.005'] += 1
    if t <= 1.010: bands['<=1.010'] += 1
    if t <= 1.020: bands['<=1.020'] += 1
    if t <= 1.030: bands['<=1.030'] += 1
    if t <= 1.050: bands['<=1.050'] += 1

two_sided = sum(1 for r in active if r['yes'] is not None and r['no'] is not None)
yes_only = sum(1 for r in rows if r['yes'] is not None and r['no'] is None)
empty = sum(1 for r in rows if r['yes'] is None and r['no'] is None)

at_sorted = sorted(active, key=lambda r: r['total'])
atl = at_sorted[0] if at_sorted else None
print(f"markets={len(markets)} active_with_total={len(at)} two_sided={two_sided} yes_only={yes_only} empty={empty}")
print(f"bands: {bands}")
if atl:
    print(f"ATL: {atl['total']:.4f} | Yes@{atl['yes']:.3f} No@{atl['no']:.3f} | liq ${atl['liq']:,.0f} | {atl['q'][:70]}")
print("--- top 10 floor ---")
for r in at_sorted[:10]:
    print(f"  {r['total']:.4f} | Y@{r['yes']:.3f} N@{r['no']:.3f} | liq ${r['liq']:,.0f} | {r['q'][:60]}")

ts = datetime.datetime.now(datetime.timezone.utc)
supp = {
    'ts': ts.isoformat(),
    'markets': len(markets),
    'active_with_total': len(at),
    'two_sided': two_sided, 'yes_only': yes_only, 'empty': empty,
    'bands': bands,
    'floor_top10': [
        {'total': round(r['total'], 4), 'yes': r['yes'], 'no': r['no'],
         'liq': r['liq'], 'q': r['q'][:80], 'slug': r['slug']}
        for r in at_sorted[:10]
    ],
}
out = f"runs/_tmp_cron_{ts.strftime('%Y%m%dT%H%M%SZ')}_supp_data.json"
with open(out, 'w') as f:
    json.dump(supp, f, indent=2)
print(f"saved: {out}")
