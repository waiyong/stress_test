"""
Configuration constants for Church Asset Risk & Stress Testing Dashboard
"""

# Church Financial Configuration
ANNUAL_OPEX_SGD = 2_400_000  # 12-month operational expenses (example)
RESERVE_MONTHS_REQUIRED = 12  # Required months of reserves

# Risk Thresholds
VOLATILITY_BREACH_THRESHOLD = 0.20  # 20% portfolio decline flag
LIQUIDITY_BREACH_DAYS = 90  # Days to access required liquidity

# Stress Test Parameter Ranges
STRESS_PARAMS = {
    "interest_rate_shock": {"min": -0.02, "max": 0.02, "default": 0.0},
    "inflation_spike": {"min": 0.02, "max": 0.08, "default": 0.035},
    "multi_asset_drawdown": {"min": -0.50, "max": -0.10, "default": -0.20},
    "redemption_freeze_days": {"min": 0, "max": 30, "default": 0},
    "early_withdrawal_penalty": {"min": -0.03, "max": 0.0, "default": -0.01},
    "counterparty_risk": {"min": 0.0, "max": 1.0, "default": 0.0}
}

# Asset Type Risk Profiles
ASSET_RISK_PROFILES = {
    "Cash_Equivalent": {
        "volatility": 0.001,
        "liquidity_days": 0,
        "interest_rate_sensitivity": 0.5
    },
    "Time_Deposit": {
        "volatility": 0.005,
        "liquidity_days": 180,  # Average
        "interest_rate_sensitivity": 0.8
    },
    "MMF": {
        "volatility": 0.02,
        "liquidity_days": 2,
        "interest_rate_sensitivity": 0.9
    },
    "Bond_Fund": {
        "volatility": 0.08,
        "liquidity_days": 5,
        "interest_rate_sensitivity": 1.2
    },
    "Multi_Asset": {
        "volatility": 0.15,
        "liquidity_days": 30,
        "interest_rate_sensitivity": 0.3
    }
}

# Market Data Configuration
CACHE_DURATION_DAYS = 7
CACHE_CLEANUP_DAYS = 14
MARKET_DATA_REFRESH_HOUR = 6  # 6 AM daily check

# Report Configuration
REPORT_TITLE = "CPC Investment Portfolio - Stress Test Analysis"
REPORT_FILENAME_PREFIX = "CPC_StressTest"

# UI Configuration
PAGE_TITLE = "Church Asset Risk & Stress Testing Dashboard"
PAGE_ICON = "📊"

# Preset Scenarios
PRESET_SCENARIOS = {
    "Conservative": {
        "interest_rate_shock": -0.005,
        "inflation_spike": 0.04,
        "multi_asset_drawdown": -0.15,
        "redemption_freeze_days": 5,
        "early_withdrawal_penalty": -0.005,
        "counterparty_risk": 0.0
    },
    "Moderate Stress": {
        "interest_rate_shock": -0.015,
        "inflation_spike": 0.06,
        "multi_asset_drawdown": -0.25,
        "redemption_freeze_days": 15,
        "early_withdrawal_penalty": -0.015,
        "counterparty_risk": 0.0
    },
    "Severe Crisis": {
        "interest_rate_shock": -0.02,
        "inflation_spike": 0.08,
        "multi_asset_drawdown": -0.40,
        "redemption_freeze_days": 30,
        "early_withdrawal_penalty": -0.025,
        "counterparty_risk": 0.05
    },
    "2008 Financial Crisis": {
        "interest_rate_shock": -0.02,
        "inflation_spike": 0.035,
        "multi_asset_drawdown": -0.37,
        "redemption_freeze_days": 21,
        "early_withdrawal_penalty": -0.02,
        "counterparty_risk": 0.02
    },
    "COVID-19 Scenario": {
        "interest_rate_shock": -0.015,
        "inflation_spike": 0.02,
        "multi_asset_drawdown": -0.33,
        "redemption_freeze_days": 14,
        "early_withdrawal_penalty": -0.01,
        "counterparty_risk": 0.0
    }
}