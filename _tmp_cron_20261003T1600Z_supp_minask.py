import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    both_priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        both_priced += 1
        # Corrected best ask: CLOB asks list is DESC-sorted, index 0 is worst
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    print(f"Best-ask supplement: {both_priced}/{len(markets)} markets both-sides-priced")
    true_brackets = [r for r in rows if r[0] < 1.0]
    print(f"TRUE BRACKETS (best-ask sum<1.00): {len(true_brackets)}")
    for r in true_brackets[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"Near-misses (<=1.005, corrected min-ask): {len(nm)}")
    for r in nm[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    if rows:
        fl = rows[0]
        print(f"Floor (min-ask sum): {fl[0]:.4f} | Yes@{fl[2]:.3f} No@{fl[3]:.3f} | {fl[1]}")

asyncio.run(supp())
