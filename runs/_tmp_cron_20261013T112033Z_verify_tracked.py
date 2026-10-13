"""Verify the tracked floor market (US unemployment 6.0%) via direct CLOB /book,
since it fell out of the top-500 active window.
gamma /public-search returns events; markets live under each event.
"""
import httpx

q = "will-us-unemployment-reach-at-least-6pt0-in-2026"
r = httpx.get(
    "https://gamma-api.polymarket.com/public-search",
    params={"q": q, "limit_per_type": 5},
    timeout=30,
)
d = r.json()
events = d.get("events", [])
markets = d.get("markets", [])
print(f"gamma public-search: events={len(events)} markets={len(markets)}")

all_markets = list(markets)
for ev in events:
    title = ev.get("title")
    active = ev.get("active")
    closed = ev.get("closed")
    print(f"\nEVENT: {title} | active={active} closed={closed}")
    for m in ev.get("markets", []) or []:
        all_markets.append(m)

print(f"\ntotal candidate markets: {len(all_markets)}")
for m in all_markets[:8]:
    qq = m.get("question")
    active = m.get("active")
    closed = m.get("closed")
    print(f"\nQ: {qq}\n  active={active} closed={closed}")
    ids = m.get("clobTokenIds")
    if isinstance(ids, str):
        ids = [x.strip().strip('"') for x in ids.strip("[]").split(",")]
    if not ids or len(ids) < 2:
        print("  (no clobTokenIds)")
        continue
    parts = []
    for tok, side in [(ids[0], "YES"), (ids[1], "NO")]:
        book = httpx.get(
            "https://clob.polymarket.com/book",
            params={"token_id": tok},
            timeout=30,
        ).json()
        asks = book.get("asks", [])
        bids = book.get("bids", [])
        ma = min(float(a["price"]) for a in asks) if asks else None
        mb = max(float(x["price"]) for x in bids) if bids else None
        print(f"  {side}: min_ask={ma} n_asks={len(asks)} max_bid={mb} n_bids={len(bids)}")
        if ma is not None:
            parts.append(ma)
    if len(parts) == 2:
        print(f"  TRUE FLOOR = {sum(parts):.4f}  (min YES ask + min NO ask)")
