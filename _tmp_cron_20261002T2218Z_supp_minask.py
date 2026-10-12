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
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            rows.append((opp.total_cost, m.question[:60], opp.yes_price, opp.no_price, 'BRACKET', opp.max_shares, m.liquidity))
            continue
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            tot = yp + np
            priced += 1
            rows.append((tot, m.question[:60], yp, np, 'minask', None, m.liquidity))
    rows.sort()
    return rows, len(markets), priced

rows, nmark, priced = asyncio.run(scan())
print(f"markets={nmark} priced={priced}")
brs = [r for r in rows if r[4]=='BRACKET']
print(f"BRACKETS(min-ask true floor <1.00): {len(brs)}")
for r in brs:
    print(f"  BRACKET sum={r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | shares={r[5]} | liq={r[6]} | {r[1]}")
print("True floor (best 10 by min-ask sum):")
for r in rows[:10]:
    print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[6]} | {r[1]}")
nm = [r for r in rows if r[0] <= 1.005 and r[4]!='BRACKET']
print(f"Near-misses (<=1.005, corrected): {len(nm)}")
