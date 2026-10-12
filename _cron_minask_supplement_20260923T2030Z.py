# Supplement: correct near-miss floor using min(asks) instead of asks[0]
# (asks[0] is worst ask due to DESC sort — known issue; detector uses min())
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    print("--- true floor (min-ask sums), bottom 8 ---")
    for t, q, yp, np_, liq in rows[:8]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"true near-misses (<=1.005): {len(nm)}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"true min-ask brackets (<1.000): {len(brackets)}")
    for t, q, yp, np_, liq in brackets[:5]:
        print(f"  🔴 {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
