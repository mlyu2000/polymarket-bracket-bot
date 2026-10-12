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
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            rows.append((opp.total_cost, m.question[:60], opp.yes_price, opp.no_price, 'BRACKET', m.liquidity, opp.net_edge, opp.max_shares))
        elif yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np_, m.question[:60], yp, np_, 'minask', m.liquidity, None, None))
    return rows

rows = asyncio.run(scan())
rows.sort()
print(f"total markets with data: {len(rows)}")
brk = [r for r in rows if r[4] == 'BRACKET']
print(f"true brackets (sum<1.00): {len(brk)}")
for r in brk:
    print(f"  BRACKET {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | edge={r[7-1]} | {r[1]}")
print("--- lowest 10 min-ask sums (true floor) ---")
for r in rows[:10]:
    print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[5]} | {r[1]}")
nm = [r for r in rows if r[4] == 'minask' and r[0] <= 1.005]
print(f"near-misses (<=1.005, min-ask): {len(nm)}")
