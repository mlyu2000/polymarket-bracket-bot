"""Supplementary near-miss scan using BEST asks (min price), not asks[0].
Polymarket CLOB /book lists asks DESC-sorted, so asks[0] is the worst price;
the verbatim cron script's near-miss block under-reports. This uses min()
consistent with detector.py logic."""
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
    secs = time.time() - t0

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        if m.liquidity is not None and m.liquidity <= 0:
            continue
        try:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
        except (KeyError, TypeError, ValueError):
            continue
        total = yp + np_
        rows.append((total, m.question[:60], yp, np_, m.liquidity))

    rows.sort()
    br = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"BEST-ASK totals computed on {len(rows)} markets in {secs:.1f}s")
    print(f"BEST-ASK sum<1.000: {len(br)}")
    for total, q, yp, np_, liq in br[:10]:
        print(f"  {total:.4f} yes@{yp:.3f} no@{np_:.3f} liq={liq} | {q}")
    print(f"BEST-ASK near-misses 1.000-1.005: {len(nm)}")
    for total, q, yp, np_, liq in nm[:10]:
        print(f"  {total:.4f} yes@{yp:.3f} no@{np_:.3f} liq={liq} | {q}")
    print("BOTTOM-12 by best-ask total:")
    for total, q, yp, np_, liq in rows[:12]:
        print(f"  {total:.4f} yes@{yp:.3f} no@{np_:.3f} liq={liq} | {q}")

asyncio.run(scan())
