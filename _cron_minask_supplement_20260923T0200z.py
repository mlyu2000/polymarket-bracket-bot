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
    dt = time.time() - t0

    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            totals.append((ya + na, m.question[:55], ya, na, m.liquidity))

    totals.sort()
    return markets, totals, dt

markets, totals, dt = asyncio.run(scan())
print(f"min-ask supplement: {len(markets)} markets in {dt:.1f}s, {len(totals)} with both books")
print(f"floor = {totals[0][0]:.4f}" if totals else "no data")
nm = [t for t in totals if t[0] <= 1.005]
print(f"near-misses (<=1.005): {len(nm)}")
for s, q, ya, na, liq in nm[:10]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
