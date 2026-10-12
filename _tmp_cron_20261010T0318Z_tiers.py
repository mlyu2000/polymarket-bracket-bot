import asyncio, logging, json
from collections import Counter
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not book.asks:
        return None
    return min(float(a['price']) for a in book.asks)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, books):
        yp, npx = best_ask(yb), best_ask(nb)
        if yp is None or npx is None:
            continue
        rows.append((yp + npx, m.question[:70], yp, npx, m.liquidity))
    rows.sort()
    print(f"priced markets: {len(rows)}")
    below1 = [r for r in rows if r[0] < 1.0]
    print(f"best-ask sums < 1.00: {len(below1)}")
    c = Counter(round(r[0], 3) for r in rows)
    print("tiers:")
    for k in sorted(c)[:6]:
        members = [r for r in rows if round(r[0], 3) == k]
        print(f"  {k:.3f} n={c[k]}")
        for t, q, yp, npx, liq in members:
            print(f"     {t:.4f} | Yes@{yp:.3f} No@{npx:.3f} | liq={liq} | {q}")
    with open('_tmp_cron_20261010T0318Z_supp_data.json', 'w') as f:
        json.dump({'priced': len(rows), 'below1': below1, 'top10': rows[:10]}, f)

asyncio.run(supp())
