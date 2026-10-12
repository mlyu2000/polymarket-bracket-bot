import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    def best_ask(book):
        return min(float(a['price']) for a in book.asks)

    def best_bid(book):
        return max(float(b['price']) for b in book.bids) if book.bids else 0.0

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            ya, na = best_ask(yb), best_ask(nb)
            total = ya + na
            rows.append((total, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    real_opps = [r for r in rows if r[0] < 1.0]
    near = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"priced markets: {priced}/{len(markets)}")
    print(f"MIN-ASK brackets (sum<1.00): {len(real_opps)}")
    for total, q, ya, na, liq in real_opps[:10]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"MIN-ASK near-misses (1.000-1.005): {len(near)}")
    for total, q, ya, na, liq in near[:10]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    if rows:
        print(f"floor: {rows[0][0]:.3f} | {rows[0][1]}")

asyncio.run(scan())
