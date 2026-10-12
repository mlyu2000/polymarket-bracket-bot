import asyncio, logging, json, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    supp = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        supp.append({'sum': round(yp + np_, 4), 'q': m.question, 'yes': yp, 'no': np_, 'liq': m.liquidity})
    supp.sort(key=lambda x: x['sum'])
    lt1 = [s for s in supp if s['sum'] < 1.00]
    band = [s for s in supp if 1.00 <= s['sum'] <= 1.005]
    runid = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = {
        'run': runid,
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'markets': len(markets),
        'priced': len(supp),
        'floor': supp[0]['sum'] if supp else None,
        'brackets_minask': len(lt1),
        'band': len(band),
        'top8': supp[:8],
        'scan_time_s': round(scan_time, 1),
    }
    with open(f'runs/scan_{runid}.json', 'w') as f:
        json.dump(out, f, indent=1)
    with open('runs/scan_latest_floor.json', 'w') as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    print(f"RUNID={runid}")

asyncio.run(main())
