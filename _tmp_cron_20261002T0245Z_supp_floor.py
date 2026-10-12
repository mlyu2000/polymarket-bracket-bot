# Floor check for cron run 2026-10-02T02:18Z — true min best-ask sum + book coverage.
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    return min(float(a['price']) for a in book.asks) if book and book.asks else None

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    sums = []
    one_sided = 0
    empty = 0
    for m, (yb, nb) in zip(markets, books):
        yp = best_ask(yb)
        np_ = best_ask(nb)
        if yp is None and np_ is None:
            empty += 1
        elif yp is None or np_ is None:
            one_sided += 1
        else:
            sums.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    sums.sort()
    print(f"markets={len(markets)} two_sided={len(sums)} one_sided={one_sided} no_asks={empty}")
    print("TOP 10 lowest best-ask sums:")
    for t, q, yp, np_, liq in sums[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if sums:
        print(f"floor={sums[0][0]:.4f}")

asyncio.run(main())
