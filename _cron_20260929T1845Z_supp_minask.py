import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
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
        priced += 1
        # CLOB /book asks are DESC-sorted -> best ask = min()
        yes_ask = min(float(a['price']) for a in yes_book.asks)
        no_ask = min(float(a['price']) for a in no_book.asks)
        rows.append((yes_ask + no_ask, m.question[:60], yes_ask, no_ask, m.liquidity))
    rows.sort()
    return rows, priced, elapsed

rows, priced, elapsed = asyncio.run(scan())
print(f"Best-ask (min) totals: {priced} priced markets in {elapsed:.1f}s")
print(f"True floor: sum={rows[0][0]:.4f}" if rows else "no priced markets")
print("Top 10 cheapest YES+NO pairs:")
for total, q, yp, np_, liq in rows[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
brackets = [r for r in rows if r[0] < 1.00]
near = [r for r in rows if 1.00 <= r[0] <= 1.005]
print(f"Brackets (sum<1.00): {len(brackets)} | Near-misses (1.00-1.005): {len(near)}")
