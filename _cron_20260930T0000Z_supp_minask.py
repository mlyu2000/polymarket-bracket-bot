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

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            rows.append((opp.total_cost, m.question[:60], opp.yes_price, opp.no_price, m.liquidity, True, opp.net_edge, opp.max_shares))
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yp = min(float(a['price']) for a in yes_book.asks)
                np_ = min(float(a['price']) for a in no_book.asks)
                rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity, False, None, None))
    return rows

rows = asyncio.run(scan())
rows.sort()
brackets = [r for r in rows if r[5]]
print(f"markets scanned: {len(rows)}")
print(f"true brackets (detector, net edge >= margin): {len(brackets)}")
for r in brackets:
    print(f"  🔴 sum={r[0]:.4f} edge={r[6]:.4f} Yes@{r[2]:.3f} No@{r[3]:.3f} shares={r[7]} liq={r[4]} | {r[1]}")
print(f"--- lowest true best-ask sums (min(price) across levels), floor check ---")
nonbr = [r for r in rows if not r[5]]
for r in nonbr[:10]:
    flag = "<1.00!" if r[0] < 1.0 else ""
    print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]} {flag}")
