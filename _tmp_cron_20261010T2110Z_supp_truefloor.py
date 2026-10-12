import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        ym = min(float(a['price']) for a in yb.asks)
        nm = min(float(a['price']) for a in nb.asks)
        rows.append((ym + nm, m.question[:60], ym, nm, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"both-ask markets: {len(rows)}")
print("10 lowest TRUE floors (min-ask YES + min-ask NO):")
for s, q, ym, nm, liq in rows[:10]:
    print(f"  {s:.4f} | Yes@{ym:.3f} No@{nm:.3f} | liq={liq} | {q}")
buckets = {'<1.00': 0, '1.00-1.005': 0, '1.005-1.01': 0, '1.01-1.02': 0, '>=1.02': 0}
for s, *_ in rows:
    if s < 1.00:
        buckets['<1.00'] += 1
    elif s < 1.005:
        buckets['1.00-1.005'] += 1
    elif s < 1.01:
        buckets['1.005-1.01'] += 1
    elif s < 1.02:
        buckets['1.01-1.02'] += 1
    else:
        buckets['>=1.02'] += 1
print(f"true-floor buckets: {buckets}")
