import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)


async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    two_sided = 0
    one_sided = 0
    sums = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            if yb and yb.asks:
                one_sided += 1
            elif nb and nb.asks:
                one_sided += 1
            continue
        two_sided += 1
        yp = float(yb.asks[0]['price'])
        np_ = float(nb.asks[0]['price'])
        sums.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    sums.sort()
    print(f"markets={len(markets)} two_sided_books={two_sided} one_sided_or_missing={one_sided}")
    print("lowest ask0 sums:")
    for total, q, yp, np_, liq in sums[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"min={sums[0][0]:.4f}" if sums else "no two-sided books")

asyncio.run(main())
