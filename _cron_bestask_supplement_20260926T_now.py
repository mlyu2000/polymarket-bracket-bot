import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    all_totals = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        all_totals.append((total, m.question[:50], m.liquidity))
        if total <= 1.005:
            rows.append((total, m.question[:50], ya, na, m.liquidity))
    rows.sort()
    all_totals.sort()
    return {'markets': len(markets), 'priced': priced, 'rows': rows, 'floor': all_totals[:5], 'dt': dt}

r = asyncio.run(supp())
print(f"Supplement (min-ask): {r['priced']}/{r['markets']} priced in {r['dt']:.1f}s")
print(f"Near-misses (min-ask sum <= 1.005): {len(r['rows'])}")
for total, q, ya, na, liq in r['rows'][:10]:
    print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print(f"Cheapest 5 books (true min-ask floor):")
for total, q, liq in r['floor']:
    print(f"  {total:.3f} | liq={liq} | {q}")
