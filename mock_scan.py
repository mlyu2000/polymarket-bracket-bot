"""
Mock scan test — validates detector against synthetic market data.

Run: python mock_scan.py
"""

from detector import BracketDetector
from models import Market, OrderBook
from config import Config


def mock_scan():
    """Scan mock markets and print detected opportunities."""
    detector = BracketDetector()

    mock_markets = [
        {
            "market_id": "market-1",
            "question": "Will BTC hit $100K by 2025?",
            "yes_ask_price": 0.47,
            "no_ask_price": 0.50,
            "yes_ask_size": 100,
            "no_ask_size": 100,
        },
        {
            "market_id": "market-2",
            "question": "Will ETH exceed $5K in 2025?",
            "yes_ask_price": 0.52,
            "no_ask_price": 0.50,
            "yes_ask_size": 100,
            "no_ask_size": 100,
        },
        {
            "market_id": "market-3",
            "question": "Will AI surpass human IQ by 2030?",
            "yes_ask_price": 0.40,
            "no_ask_price": 0.55,
            "yes_ask_size": 20,
            "no_ask_size": 200,
        },
    ]

    print(f"Scanning {len(mock_markets)} mock markets...")
    print(f"Config: margin={Config.MIN_PROFIT_MARGIN}, fee_buf={Config.FEE_BUFFER}, slip_buf={Config.SLIPPAGE_BUFFER}\n")

    found = 0
    for m in mock_markets:
        market = Market(
            id=m["market_id"],
            question=m["question"],
            condition_id=f"0x{m['market_id']}",
            slug=m["market_id"],
            active=True,
            closed=False,
            outcomes=["Yes", "No"],
            outcome_prices=[m["yes_ask_price"], m["no_ask_price"]],
            clob_token_ids=[f"{m['market_id']}_yes", f"{m['market_id']}_no"],
            volume=100000,
            liquidity=50000,
        )

        yes_book = OrderBook(
            market=m["market_id"],
            asset_id=f"{m['market_id']}_yes",
            bids=[],
            asks=[{"price": str(m["yes_ask_price"]), "size": str(m["yes_ask_size"])}],
            min_order_size="5",
            tick_size="0.01",
        )

        no_book = OrderBook(
            market=m["market_id"],
            asset_id=f"{m['market_id']}_no",
            bids=[],
            asks=[{"price": str(m["no_ask_price"]), "size": str(m["no_ask_size"])}],
            min_order_size="5",
            tick_size="0.01",
        )

        opp = detector.detect(market, yes_book, no_book)

        if opp:
            found += 1
            print(detector.format_opportunity(opp))
            print()

    print(f"\nScan complete: {found} opportunity(ies) found out of {len(mock_markets)} markets.")


if __name__ == "__main__":
    mock_scan()
