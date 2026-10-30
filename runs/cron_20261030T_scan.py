"""Scheduled cron scan: bracket opportunity detection + paper execution."""
import asyncio, logging, time, json, os
from datetime import datetime, timezone
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity
            })
            paper_result = paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'paper_stats': paper.stats,
    }

result = asyncio.run(scan())
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"✅ BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"📊 Near-misses (≤1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

# Persist
out_path = f"runs/_tmp_cron_{ts}_scan_out.txt"
data_path = f"runs/_tmp_cron_{ts}_supp_data.json"
with open(out_path, "w") as f:
    f.write(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s\n")
    f.write(f"BRACKETS: {len(result['opps'])}\n")
    for o in result['opps']:
        f.write(f"  {o['sum']:.3f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} sh={o['shares']} liq={o['liq']} | {o['q']}\n")
    f.write(f"NEAR_MISSES: {len(result['near_misses'])}\n")
    for total, q, yp, np, liq in result['near_misses']:
        f.write(f"  {total:.3f} Yes@{yp:.3f} No@{np:.3f} liq={liq} | {q}\n")
with open(data_path, "w") as f:
    json.dump(result, f, indent=2)

# Log to index
if os.path.exists("runs/index.jsonl"):
    with open("runs/index.jsonl", "r") as f:
        lines = f.readlines()
    last_num = 0
    for line in lines:
        d = json.loads(line)
        last_num = d.get("run_num", 0)
    new_num = last_num + 1
else:
    new_num = 1
entry = {"run_num": new_num, "ts": ts, "markets": result['markets'], "scan_time": round(result['scan_time'],1), "brackets": len(result['opps']), "near_misses": len(result['near_misses']), "out_file": out_path, "data_file": data_path, "paper_stats": result['paper_stats']}
with open("runs/index.jsonl", "a") as f:
    f.write(json.dumps(entry) + "\n")

summary = f"polymarket bracket scan {ts}: {result['markets']} markets, {len(result['opps'])} brackets, {len(result['near_misses'])} near-misses"
print(summary)
