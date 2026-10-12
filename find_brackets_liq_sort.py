import asyncio
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from config import Config
from paper_executor import PaperExecutor
import time

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()
    # fetch markets with liquidity ascending
    # Temporarily change config
    orig_sort = Config.SCAN_SORT_BY
    Config.SCAN_SORT_BY = "liquidity"
    # Need to reload? The fetch uses Config.SCAN_SORT_BY at runtime
    markets = await api.fetch_active_markets(limit=500)
    Config.SCAN_SORT_BY = orig_sort
    print(f"Fetched {len(markets)} markets")
    opps = []
    for m in markets:
        if m.liquidity <= 0:
            continue
        yb = await api.fetch_order_book(m.clob_token_ids[0])
        nb = await api.fetch_order_book(m.clob_token_ids[1])
        if not yb or not nb:
            continue
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append(opp)
            print(f"FOUND {opp.total_cost:.4f} {m.question[:60]}")
    print(f"Total opps: {len(opps)}")

asyncio.run(scan())
