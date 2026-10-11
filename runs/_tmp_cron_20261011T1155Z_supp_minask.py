import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    two_sided = 0
    one_sided_yes_only = 0
    one_sided_no_only = 0
    both_empty = 0
    floors = []
    for m, (yb, nb) in zip(markets, all_books):
        ya = [float(a['price']) for a in (yb.asks if yb and yb.asks else [])]
        na = [float(a['price']) for a in (nb.asks if nb and nb.asks else [])]
        if ya and na:
            two_sided += 1
            floors.append((min(ya) + min(na), m.question[:60], min(ya), min(na), m.liquidity))
        elif ya:
            one_sided_yes_only += 1
        elif na:
            one_sided_no_only += 1
        else:
            both_empty += 1

    floors.sort()
    print(f"markets={len(markets)} two_sided={two_sided} one_sided_yes_only={one_sided_yes_only} one_sided_no_only={one_sided_no_only} both_empty={both_empty}")
    print("TRUE FLOOR (min-ask) top 8:")
    for f in floors[:8]:
        print(f"  {f[0]:.4f} | Yes@{f[2]:.3f} No@{f[3]:.3f} | liq {f[4]:.2f} | {f[1]}")
    if floors:
        print(f"floor_min={floors[0][0]:.4f} floor_median={floors[len(floors)//2][0]:.4f}")
        actionable = [f for f in floors if f[0] < 0.98]
        print(f"actionable(<0.98): {len(actionable)}")
        for f in actionable[:10]:
            print(f"  ACTIONABLE {f[0]:.4f} | {f[1]}")

    out = {
        "ts": "20261011T1155Z",
        "markets": len(markets),
        "scan_time_s": 54.0,
        "brackets": 0,
        "paper_executions": 0,
        "near_misses_le_1.005": 0,
        "near_miss_note": "cron-script near-miss block uses asks[0] (DESC artifact, known broken); true floor computed via min-ask supplement",
        "book_shape": {
            "two_sided": two_sided,
            "one_sided_yes_only": one_sided_yes_only,
            "one_sided_no_only": one_sided_no_only,
            "both_empty": both_empty,
        },
        "floor_min": floors[0][0] if floors else None,
        "floor_median": floors[len(floors)//2][0] if floors else None,
        "actionable_lt_098": len([f for f in floors if f[0] < 0.98]) if floors else 0,
        "floors_top8": [
            {"total": f[0], "q": f[1], "yes": f[2], "no": f[3], "liq": f[4]}
            for f in floors[:8]
        ],
        "floor_dist_1.005": len([f for f in floors if f[0] <= 1.005]) if floors else 0,
    }
    with open("runs/_tmp_cron_20261011T1155Z_supp_data.json", "w") as fh:
        json.dump(out, fh, indent=2)

asyncio.run(main())
