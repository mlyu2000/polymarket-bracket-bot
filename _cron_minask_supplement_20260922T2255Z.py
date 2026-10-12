import asyncio, logging, time
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
    dt = time.time() - t0
    minask = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            cy = min(float(a['price']) for a in yes_book.asks)
            cn = min(float(a['price']) for a in no_book.asks)
            minask.append({'sum': round(cy + cn, 6), 'q': m.question[:60], 'yes': cy, 'no': cn, 'liq': m.liquidity})
    minask.sort(key=lambda d: d['sum'])
    return len(markets), minask, dt

n, minask, dt = asyncio.run(scan())
print(f"Markets: {n} in {dt:.1f}s | priced pairs: {len(minask)}")
print("MIN-ASK FLOOR top 10:")
for d in minask[:10]:
    print(f"  {d['sum']:.3f} | Y@{d['yes']:.3f} N@{d['no']:.3f} | liq={d['liq']} | {d['q']}")
nl = [d for d in minask if d['sum'] <= 1.005]
print(f"MIN-ASK near-misses (<=1.005): {len(nl)}")
for d in nl[:10]:
    print(f"  {d['sum']:.3f} | Y@{d['yes']:.3f} N@{d['no']:.3f} | liq={d['liq']} | {d['q']}")
lt1 = [d for d in minask if d['sum'] < 1.0]
print(f"TRUE BRACKETS (min-ask sum < 1.0): {len(lt1)}")
for d in lt1:
    print(f"  {d['sum']:.3f} | Y@{d['yes']:.3f} N@{d['no']:.3f} | {d['q']}")
