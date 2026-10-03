import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    both_priced = 0
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        if m.liquidity <= 0:
            continue
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        total = yes_min + no_min
        both_priced += 1
        rows.append((total, m.question[:60], round(yes_min, 3), round(no_min, 3), m.liquidity))

    rows.sort()
    print(f"both-sides-priced (liq>0): {both_priced}")
    print("TRUE best-ask floor sums (min over levels):")
    for total, q, yp, np, liq in rows[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    sub1 = [r for r in rows if r[0] < 1.0]
    print(f"sums < 1.000: {len(sub1)}")
    for total, q, yp, np, liq in sub1[:5]:
        print(f"  🔴 {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    with open('_tmp_cron_20261003T1635Z_supp_data.json', 'w') as f:
        json.dump({'both_priced': both_priced,
                   'floor_rows': [list(r) for r in rows[:8]],
                   'sub1_count': len(sub1)}, f, indent=1)

asyncio.run(supp())
