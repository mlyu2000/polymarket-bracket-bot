import asyncio, logging, json
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
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        yp, np = best_ask(yb), best_ask(nb)
        if yp is None or np is None:
            continue
        priced += 1
        rows.append((yp + np, m.question[:70], yp, np, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    below1 = [r for r in rows if r[0] < 1.0]
    print(f"best-ask sums < 1.00: {len(below1)}")
    for t, q, yp, np, liq in below1[:10]:
        print(f"  <1.00  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print("closest 8 by best-ask sum:")
    for t, q, yp, np, liq in rows[:8]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    with open('_tmp_cron_20261010T0022Z_supp_data.json', 'w') as f:
        json.dump({'priced': priced, 'below1': below1, 'top8': rows[:8]}, f, indent=1)

asyncio.run(supp())
