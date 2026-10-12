import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not getattr(book, 'asks', None):
        return None
    return min(float(a['price']) for a in book.asks)

async def scan():
    t0 = time.time()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    brackets = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        y = best_ask(yes_book)
        n = best_ask(no_book)
        if y is None or n is None:
            continue
        priced += 1
        total = y + n
        brackets.append({'sum': round(total, 4), 'q': m.question[:60], 'yes': y, 'no': n, 'liq': m.liquidity})

    brackets.sort(key=lambda r: r['sum'])
    return markets, priced, brackets, scan_time

result = asyncio.run(scan())
markets, priced, brackets, scan_time = result
floor = brackets[0]['sum'] if brackets else None
band = sum(1 for r in brackets if r['sum'] <= 1.005)
print(f"[MINASK] markets={len(markets)} priced={priced} floor={floor} band<=1.005={band} true_brackets={sum(1 for r in brackets if r['sum']<1.0)} time={scan_time:.1f}s")
for r in brackets[:8]:
    print(f"  {r['sum']:.4f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")

with open('_tmp_cron_20261008T0817Z_supp_data.json', 'w') as f:
    json.dump({'markets': len(markets), 'priced': priced, 'floor': floor, 'band': band,
               'top8': brackets[:8], 'band_rows': [r for r in brackets if r['sum'] <= 1.005],
               'scan_time_s': round(scan_time, 1)}, f, indent=1)
