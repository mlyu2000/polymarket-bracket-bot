import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        # True best ask = MIN across all ask levels (asks are DESC-sorted, asks[0] is worst)
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        rows.append({'sum': round(yp+np, 6), 'yes': yp, 'no': np,
                     'q': m.question[:70], 'liq': m.liquidity,
                     'ydepth': sum(float(a['size']) for a in yes_book.asks),
                     'ndepth': sum(float(a['size']) for a in no_book.asks)})
    rows.sort(key=lambda r: r['sum'])
    return rows

rows = asyncio.run(supp())
print(f"markets with both books: {len(rows)}")
print(f"true floor (min sum): {rows[0]['sum']:.3f}" if rows else "no data")
print("--- top 10 lowest best-ask sums ---")
for r in rows[:10]:
    print(f"  {r['sum']:.3f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | ydepth={r['ydepth']:.0f} ndepth={r['ndepth']:.0f} | {r['q']}")
br = [r for r in rows if r['sum'] < 1.0]
print(f"--- sums < 1.000 (true brackets): {len(br)} ---")
for r in br:
    print(f"  {r['sum']:.3f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")
