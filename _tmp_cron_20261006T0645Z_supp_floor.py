import asyncio, logging, time, json
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

    opps = []
    near = []
    min_sums = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append([opp.total_cost, opp.net_edge, m.question[:60]])
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            min_sums.append([round(total, 6), m.question[:60], yp, np_, m.liquidity])
            if total <= 1.005:
                near.append([round(total, 6), m.question[:60], yp, np_, m.liquidity])

    min_sums.sort()
    near.sort()
    return {'markets': len(markets), 'opps': opps, 'near': near, 'top': min_sums[:10], 'priced': priced}

result = asyncio.run(scan())
print(f"priced={result['priced']} of {result['markets']}; brackets={len(result['opps'])}; band<=1.005={len(result['near'])}")
for r in result['near']:
    print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
print("top-5 true sums:")
for r in result['top'][:5]:
    print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
with open('_tmp_cron_20261006T0645Z_supp_data.json', 'w') as f:
    json.dump({'priced': result['priced'], 'top': result['top'], 'near': result['near'], 'opps': result['opps']}, f)
