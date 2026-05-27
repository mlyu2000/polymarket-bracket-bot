"""
Tests for config validation.
"""

import pytest
import os
from unittest.mock import patch

from config import Config


class TestConfigDefaults:
    """Test default config values."""

    def test_default_execution_mode(self):
        assert Config.EXECUTION_MODE == "dry_run"

    def test_default_min_profit_margin(self):
        assert Config.MIN_PROFIT_MARGIN == 0.01

    def test_default_max_capital(self):
        assert Config.MAX_CAPITAL_PER_TRADE == 50.0

    def test_default_fee_buffer(self):
        assert Config.FEE_BUFFER == 0.005

    def test_default_slippage_buffer(self):
        assert Config.SLIPPAGE_BUFFER == 0.005

    def test_default_poll_interval(self):
        assert Config.POLL_INTERVAL_SECONDS == 5.0

    def test_default_max_markets(self):
        assert Config.MAX_MARKETS_PER_SCAN == 100

    def test_default_min_liquidity(self):
        assert Config.MIN_LIQUIDITY_USDC == 1000.0

    def test_default_api_bases(self):
        assert Config.GAMMA_API_BASE == "https://gamma-api.polymarket.com"
        assert Config.CLOB_API_BASE == "https://clob.polymarket.com"
        assert Config.DATA_API_BASE == "https://data-api.polymarket.com"


class TestConfigValidation:
    """Test config validation logic."""

    def test_valid_config_passes(self):
        Config.validate()  # Should not raise

    def test_invalid_execution_mode(self):
        with patch.object(Config, "EXECUTION_MODE", "invalid"):
            with pytest.raises(ValueError, match="Invalid EXECUTION_MODE"):
                Config.validate()

    def test_negative_min_profit_margin(self):
        with patch.object(Config, "MIN_PROFIT_MARGIN", -0.01):
            with pytest.raises(ValueError, match="MIN_PROFIT_MARGIN must be > 0"):
                Config.validate()

    def test_zero_min_profit_margin(self):
        with patch.object(Config, "MIN_PROFIT_MARGIN", 0):
            with pytest.raises(ValueError, match="MIN_PROFIT_MARGIN must be > 0"):
                Config.validate()

    def test_negative_max_capital(self):
        with patch.object(Config, "MAX_CAPITAL_PER_TRADE", -10):
            with pytest.raises(ValueError, match="MAX_CAPITAL_PER_TRADE must be > 0"):
                Config.validate()

    def test_zero_max_capital(self):
        with patch.object(Config, "MAX_CAPITAL_PER_TRADE", 0):
            with pytest.raises(ValueError, match="MAX_CAPITAL_PER_TRADE must be > 0"):
                Config.validate()

    def test_poll_interval_less_than_one(self):
        with patch.object(Config, "POLL_INTERVAL_SECONDS", 0):
            with pytest.raises(ValueError, match="POLL_INTERVAL_SECONDS must be >= 1"):
                Config.validate()

    def test_negative_fee_buffer(self):
        with patch.object(Config, "FEE_BUFFER", -0.01):
            with pytest.raises(ValueError, match="FEE_BUFFER must be >= 0"):
                Config.validate()

    def test_negative_slippage_buffer(self):
        with patch.object(Config, "SLIPPAGE_BUFFER", -0.01):
            with pytest.raises(ValueError, match="SLIPPAGE_BUFFER must be >= 0"):
                Config.validate()

    def test_live_mode_valid(self):
        with patch.object(Config, "EXECUTION_MODE", "live"):
            Config.validate()  # Should not raise

    def test_zero_markets_per_scan(self):
        with patch.object(Config, "MAX_MARKETS_PER_SCAN", 0):
            with pytest.raises(ValueError, match="MAX_MARKETS_PER_SCAN must be >= 1"):
                Config.validate()

    def test_negative_markets_per_scan(self):
        with patch.object(Config, "MAX_MARKETS_PER_SCAN", -5):
            with pytest.raises(ValueError, match="MAX_MARKETS_PER_SCAN must be >= 1"):
                Config.validate()
