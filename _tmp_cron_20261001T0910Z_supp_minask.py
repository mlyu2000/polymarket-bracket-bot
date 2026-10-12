# Supplementary: near-misses computed with BEST ask (min price), since the
# verbatim cron script's asks[0] is the WORST ask (CLOB asks are DESC-sorted).
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

    near = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        if total < 1.0:
            brackets.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:60], yp, np_, m.liquidity))
    brackets.sort()
    near.sort()
    print(f"[best-ask] markets: {len(markets)}")
    print(f"[best-ask] true brackets (sum<1.00): {len(brackets)}")
    for t, q, yp, np_, liq in brackets[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"[best-ask] near-misses (1.000<sum<=1.005): {len(near)}")
    for t, q, yp, np_, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
