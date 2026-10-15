# Supplementary: corrected near-miss computation using best ask = min(asks)
# (asks[0] in CLOB payload is the WORST ask, desc-sorted; see memory note)
import asyncio, logging, time, json, datetime
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    near = []
    tiers_list = []
    with_both = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if not m.active or m.closed or m.liquidity <= 0:
            continue
        with_both += 1
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        tiers_list.append((total, m.question[:50], yp, np, m.liquidity))
        if total <= 1.005:
            near.append((total, m.question[:50], yp, np, m.liquidity))
    near.sort()
    tiers_list.sort()
    print(f"⏱ corr. scan {dt:.1}s | markets={len(markets)} both-asks={with_both}")
    print(f"📊 NEAR-MISSES (best-ask min(), sum<=1.005): {len(near)}")
    for total, q, yp, np, liq in near[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
    tiers = {
        '<=1.050': sum(1 for n in tiers_list if n[0] <= 1.050),
        '<=1.020': sum(1 for n in tiers_list if n[0] <= 1.020),
        '<=1.010': sum(1 for n in tiers_list if n[0] <= 1.010),
        '<=1.005': sum(1 for n in tiers_list if n[0] <= 1.005),
        '<1.000': sum(1 for n in tiers_list if n[0] < 1.000),
    }
    print(f"TIERS: {tiers}")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    data = {
        'ts': ts, 'markets': len(markets), 'with_both_asks': with_both,
        'two_sided': with_both, 'not_bracketable': len(markets) - with_both,
        'tiers': tiers,
        'top25': [{'total': n[0], 'q': n[1], 'yes': n[2], 'no': n[3], 'liq': n[4]} for n in near[:25]],
    }
    with open(f'runs/_tmp_cron_{ts[:13].replace("-", "").replace(":", "")}Z_supp_data.json', 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"persisted to runs/_tmp_cron_*_supp_data.json")
    return near

asyncio.run(scan())
