# Supplementary near-miss check using BEST asks (min price), matching detector.py logic.
# The verbatim cron script uses asks[0], which on Polymarket CLOB is the WORST ask
# (asks are DESC-sorted), so its near-miss list always reports sum ~= 1.998 (0 hits).
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    return len(markets), rows

markets_n, rows = asyncio.run(scan())
print(f"best-ask scan over {markets_n} markets")
nm = [r for r in rows if r[0] <= 1.005]
print(f"best-ask near-misses (<=1.005): {len(nm)}")
for total, q, yp, np_, liq in nm[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"true floor: {rows[0][0]:.3f} | {rows[0][1]}")
