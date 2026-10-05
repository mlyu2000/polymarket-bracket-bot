import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    both = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(yes_ask["price"]); np_ = float(no_ask["price"])
        total = yp + np_
        both += 1
        rows.append((total, m.question[:60], yp, np_, m.liquidity,
                     int(float(yes_ask["size"])), int(float(no_ask["size"]))))
    rows.sort()
    print(f"markets={len(markets)} both_sides_priced={both} scan_time={scan_time:.1f}s")
    print("top12 best-ask totals:")
    for r in rows[:12]:
        print(f"  {r[0]:.3f} | yes {r[2]:.3f} x{r[5]} no {r[3]:.3f} x{r[6]} | liq {r[4]} | {r[1]}")
    brackets = [r for r in rows if r[0] < 1.000]
    print(f"best-ask brackets (<1.000): {len(brackets)}")
    for r in brackets:
        print(f"  BRACKET {r[0]:.3f} | yes {r[2]:.3f} no {r[3]:.3f} | {r[1]}")
    band = [r for r in rows if r[0] <= 1.010]
    print(f"band <=1.010 count: {len(band)}")
    import json
    with open('_tmp_cron_20261005T0810Z_supp_data.json', 'w') as f:
        json.dump([{'total': r[0], 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4],
                    'yes_size': r[5], 'no_size': r[6]} for r in rows[:30]], f, indent=1)

asyncio.run(scan())
