import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def diag():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    print(f"Scan: {len(markets)} markets in {time.time()-t0:.1f}s")

    rows = []
    two_sided = yes_only = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book):
            continue
        ya = yes_book.asks
        na = no_book.asks
        if not ya and not na:
            continue
        if ya and na:
            two_sided += 1
            yp = min(float(a['price']) for a in ya)
            np_ = min(float(a['price']) for a in na)
            total = yp + np_
            rows.append((total, m.question[:55], yp, np_, m.liquidity, ya[0]['price'], na[0]['price']))
        else:
            yes_only += 1

    rows.sort()
    print(f"two-sided: {two_sided} | yes_only/no_only: {yes_only} | NOT bracket-able: "
          f"{len(markets)-two_sided}/{len(markets)} ({100*(len(markets)-two_sided)/len(markets):.0f}%)")
    print("\n--- TOP 10 by min-ask floor (min(yes)+min(no)) ---")
    for total, q, yp, np_, liq, ya0, na0 in rows[:10]:
        flag = " 🔴BRACKET" if total < 1.0 else ""
        print(f"{total:.3f}{flag} | Y@{yp:.3f} N@{np_:.3f} | liq {liq} | asks0 Y={ya0} N={na0} | {q}")

    import json
    ts = time.strftime("%Y%m%d_%H%MZ", time.gmtime())
    out = {
        'ts_utc': ts, 'markets': len(markets),
        'two_sided': two_sided, 'yes_only': yes_only,
        'not_bracketable_pct': round(100*(len(markets)-two_sided)/len(markets), 1),
        'floor': rows[0][0] if rows else None,
        'top10': [{'total': r[0], 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]} for r in rows[:10]],
    }
    with open(f"runs/_tmp_cron_{ts}_supp_data.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nPersisted: runs/_tmp_cron_{ts}_supp_data.json")

asyncio.run(diag())
