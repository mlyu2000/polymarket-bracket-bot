import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor
logging.basicConfig(level=logging.ERROR)
async def scan():
    Config.validate()
    api = PolymarketAPI(); detector = BracketDetector(); paper = PaperExecutor()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0
    opps=[]; near=[]
    for m,(yb,nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append({'q':m.question[:60],'yes':opp.yes_price,'no':opp.no_price,'sum':opp.total_cost,'edge':opp.net_edge,'shares':opp.max_shares,'liq':m.liquidity})
            paper.execute(opp)
        elif yb and nb and yb.asks and nb.asks:
            yp=float(yb.asks[0]['price']); np_=float(nb.asks[0]['price']); t=yp+np_
            if t<=1.005: near.append((t,m.question[:50],yp,np_,m.liquidity))
    near.sort()
    return {'markets':len(markets),'opps':opps,'near_misses':near,'scan_time':scan_time}
r=asyncio.run(scan())
print(f"Scan: {r['markets']} markets in {r['scan_time']:.1f}s")
print(f"BRACKETS (sum<1.00): {len(r['opps'])}")
for o in r['opps']:
    print(f"  {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"Near-misses (<=1.005): {len(r['near_misses'])}")
for t,q,yp,np_,liq in r['near_misses'][:5]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
