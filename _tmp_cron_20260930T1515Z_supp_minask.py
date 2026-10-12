# Supplemental: correct near-miss floor using min() over asks
# (asks are DESC-sorted from /book; asks[0] is the worst ask, not the best)
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    true_brackets = []
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            true_brackets.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))

    rows.sort()
    priced = len(rows)
    print(f"markets={len(markets)} priced_pairs={priced} detector_brackets={len(true_brackets)}")
    for o in true_brackets:
        print(f"  BRACKET sum={o.total_cost:.4f} edge={o.net_edge:.4f} yes={o.yes_price} no={o.no_price} q={o.market.question[:60]}")
    print("TOP 10 BEST-ASK SUMS (min over asks):")
    for total, q, yp, np_, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    lt1 = sum(1 for r in rows if r[0] < 1.0)
    le1005 = sum(1 for r in rows if r[0] <= 1.005)
    print(f"count(sum<1.00)={lt1}  count(sum<=1.005)={le1005}")

asyncio.run(scan())
