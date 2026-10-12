import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            totals.append((yp + np, m.question[:55], yp, np, m.liquidity))
    totals.sort()
    return totals

totals = asyncio.run(supp())
print(f"markets with two-sided asks: {len(totals)}")
print(f"true floor (min sum): {totals[0][0]:.4f}" if totals else "no totals")
nm = [t for t in totals if t[0] <= 1.005]
print(f"NEAR-MISSES (best-ask sum <= 1.005): {len(nm)}")
for total, q, yp, np, liq in nm[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("--- next 5 closest above 1.005 ---")
for total, q, yp, np, liq in nm[10:15] if len(nm)>15 else totals[len(nm):len(nm)+5]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
