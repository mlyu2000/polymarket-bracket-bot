"""
Tests for Polymarket API client.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
import httpx

from polymarket_api import PolymarketAPI
from models import Market, OrderBook


@pytest.fixture
def api():
    return PolymarketAPI()


@pytest.mark.asyncio
async def test_fetch_active_markets_parse_response(api):
    """Test market parsing from Gamma API response."""
    mock_response = [
        {
            "id": "1",
            "question": "Will X happen?",
            "conditionId": "0xabc",
            "slug": "will-x-happen",
            "active": True,
            "closed": False,
            "outcomes": json.dumps(["Yes", "No"]),
            "outcomePrices": json.dumps(["0.50", "0.50"]),
            "clobTokenIds": json.dumps(["yes_1", "no_1"]),
            "volume": 100000,
            "liquidity": 50000,
            "endDate": "2025-12-31",
            "category": "politics",
        }
    ]

    with patch.object(api, "_request", new_callable=AsyncMock, return_value=mock_response):
        markets = await api.fetch_active_markets()

    assert len(markets) == 1
    m = markets[0]
    assert m.question == "Will X happen?"
    assert m.active is True
    assert m.closed is False
    assert m.outcomes == ["Yes", "No"]
    assert m.outcome_prices == [0.50, 0.50]
    assert m.clob_token_ids == ["yes_1", "no_1"]


@pytest.mark.asyncio
async def test_fetch_active_markets_filter_non_binary(api):
    """Test non-binary markets are filtered out."""
    mock_response = [
        {
            "id": "1",
            "question": "Who will win?",
            "conditionId": "0xabc",
            "slug": "who-wins",
            "active": True,
            "closed": False,
            "outcomes": json.dumps(["A", "B", "C"]),  # 3 outcomes
            "outcomePrices": json.dumps(["0.33", "0.33", "0.34"]),
            "clobTokenIds": json.dumps(["a_1", "b_1", "c_1"]),
            "volume": 100000,
            "liquidity": 50000,
        }
    ]

    with patch.object(api, "_request", new_callable=AsyncMock, return_value=mock_response):
        markets = await api.fetch_active_markets()

    assert len(markets) == 0


@pytest.mark.asyncio
async def test_fetch_order_book_success(api):
    """Test order book parsing from CLOB API."""
    mock_response = {
        "market": "0xabc",
        "asset_id": "yes_1",
        "bids": [{"price": "0.44", "size": "500"}],
        "asks": [{"price": "0.46", "size": "300"}],
        "min_order_size": "5",
        "tick_size": "0.01",
        "last_trade_price": "0.45",
    }

    with patch.object(api, "_request", new_callable=AsyncMock, return_value=mock_response):
        book = await api.fetch_order_book("yes_1")

    assert book is not None
    assert book.asset_id == "yes_1"
    assert len(book.bids) == 1
    assert len(book.asks) == 1
    assert book.last_trade_price == "0.45"


@pytest.mark.asyncio
async def test_fetch_order_book_failure(api):
    """Test order book returns None on failure."""
    with patch.object(api, "_request", side_effect=Exception("Network error")):
        book = await api.fetch_order_book("yes_1")

    assert book is None


@pytest.mark.asyncio
async def test_fetch_order_books_parallel(api):
    """Test parallel order book fetching."""
    yes_response = {
        "market": "0xabc",
        "asset_id": "yes_1",
        "bids": [],
        "asks": [{"price": "0.46", "size": "300"}],
        "min_order_size": "5",
        "tick_size": "0.01",
    }
    no_response = {
        "market": "0xabc",
        "asset_id": "no_1",
        "bids": [],
        "asks": [{"price": "0.50", "size": "200"}],
        "min_order_size": "5",
        "tick_size": "0.01",
    }

    async def mock_request(url):
        if "yes_1" in url:
            return yes_response
        return no_response

    with patch.object(api, "_request", new=mock_request):
        yes_book, no_book = await api.fetch_order_books_parallel("yes_1", "no_1")

    assert yes_book is not None
    assert no_book is not None
    assert yes_book.asset_id == "yes_1"
    assert no_book.asset_id == "no_1"


@pytest.mark.asyncio
async def test_request_429_backoff(api):
    """Test _request handles 429 and retries."""
    call_count = 0
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"ok": True}

    async def mock_get(url):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            resp_429 = MagicMock()
            resp_429.status_code = 429
            return resp_429
        return mock_resp

    mock_client = AsyncMock()
    mock_client.get = mock_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch("asyncio.sleep", new_callable=AsyncMock):
        result = await api._request("http://example.com")

    assert result == {"ok": True}
    assert call_count == 3  # Initial + 2 retries


@pytest.mark.asyncio
async def test_request_500_backoff(api):
    """Test _request handles 500 errors and retries."""
    call_count = 0
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"ok": True}

    async def mock_get(url):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise httpx.HTTPStatusError("Server Error", request=MagicMock(), response=MagicMock(status_code=500))
        return mock_resp

    mock_client = AsyncMock()
    mock_client.get = mock_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch("asyncio.sleep", new_callable=AsyncMock):
        result = await api._request("http://example.com")

    assert result == {"ok": True}
    assert call_count == 3


@pytest.mark.asyncio
async def test_request_exceeds_max_retries(api):
    """Test _request raises after max retries on 429."""
    mock_client = AsyncMock()
    async def mock_get(url):
        resp_429 = MagicMock()
        resp_429.status_code = 429
        return resp_429
    mock_client.get = mock_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch("asyncio.sleep", new_callable=AsyncMock), \
         patch.object(api, "max_retries", 2):
        with pytest.raises(RuntimeError, match="Rate limited"):
            await api._request("http://example.com")


@pytest.mark.asyncio
async def test_rate_limit_backoff(api):
    """Test rate limit backoff configuration."""
    # Simpler: verify backoff config
    assert api.backoff_base == 2.0
    assert api.max_retries == 3


@pytest.mark.asyncio
async def test_double_encoded_json_fields(api):
    """Test double-encoded JSON fields are parsed correctly."""
    mock_response = [
        {
            "id": "1",
            "question": "Test market",
            "conditionId": "0xabc",
            "slug": "test",
            "active": True,
            "closed": False,
            "outcomes": json.dumps(["Yes", "No"]),
            "outcomePrices": json.dumps(["0.45", "0.55"]),
            "clobTokenIds": json.dumps(["token_1", "token_2"]),
            "volume": 50000,
            "liquidity": 20000,
        }
    ]

    with patch.object(api, "_request", new_callable=AsyncMock, return_value=mock_response):
        markets = await api.fetch_active_markets()

    assert len(markets) == 1
    m = markets[0]
    assert isinstance(m.outcomes, list)
    assert isinstance(m.outcome_prices, list)
    assert isinstance(m.clob_token_ids, list)
    assert m.outcome_prices[0] == 0.45
