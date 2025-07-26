# 🛠️ Development

## Quick Navigation
- [← Back to Main Documentation](../)
- [API Reference](#api-reference) - Code documentation and interfaces
- [Deployment Guide](#deployment) - Production deployment procedures

## Overview

This section provides comprehensive resources for developers and maintainers of the Church Asset Risk Dashboard, including API documentation, deployment procedures, and development best practices.

## 🏗️ Development Environment

### Prerequisites
- Python 3.8+
- Virtual environment: `source venv/bin/activate` (REQUIRED)
- Git for version control
- OpenBB Platform for market data

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd stress_testing

# Environment setup (CRITICAL)
source venv/bin/activate
pip install -r requirements.txt

# Verify installation
python -c "from utils.enhanced_data_sources import get_enhanced_data_manager; print('✅ Ready')"

# Run development server
streamlit run app.py
```

## 📚 API Reference

### Core Modules

#### `utils/enhanced_data_sources.py`
**Primary data pipeline with intelligent hybrid backfill**

```python
class EnhancedDataSourceManager:
    def __init__(cache_dir: str = "data/market_cache"):
        # data_quality_threshold_days = 180  # NEW: Hybrid backfill threshold
    
    def fetch_market_data(force_refresh=False, incremental=True) -> Dict[str, Any]
    def set_backfill_start_date(start_date: str) -> None  # NEW: Dynamic start date
    def get_asset_history(asset_type: str, asset_name: str, days: int = 30) -> Optional[Dict]
    def cleanup_old_data(days_to_keep: int = 90) -> None
    
    # NEW: Internal hybrid logic methods
    def _get_existing_data_age_days() -> int
    def _get_existing_coverage(index_name: str) -> Optional[Dict]

# Factory function
def get_enhanced_data_manager() -> EnhancedDataSourceManager
```

**Key Methods**:
- `fetch_market_data()`: **Intelligent hybrid backfill** with 180-day quality threshold
- `set_backfill_start_date()`: **NEW**: Configure custom start dates for backfill
- `get_asset_history()`: Historical data access for specific assets
- `cleanup_old_data()`: Maintenance and cleanup operations

**Hybrid Backfill Logic**:
- **<180 days old data**: Incremental gap filling (50 API calls, 10 seconds)
- **>180 days old data**: Full refresh for data quality (1000 API calls, 45 seconds)

#### `utils/asset_data_manager.py`
**Asset-based storage management**

```python
class AssetDataManager:
    def save_singapore_rates(rates_data: Dict, date_str: str) -> None
    def save_index_data(index_name: str, index_data: Dict, date_str: str) -> None
    def save_currency_data(currency_pair: str, rates_data: Dict, date_str: str) -> None
    def get_current_market_data() -> Dict[str, Any]
    def update_metadata(update_type: str) -> None
```

**Storage Structure**:
- Asset-specific files in `data/market_cache/{asset_type}/`
- Current data hot cache in `data/market_cache/current/`
- Metadata tracking in `data/market_cache/metadata/`

#### `utils/risk_engine.py`
**Core stress testing calculations**

```python
class RiskEngine:
    def __init__(portfolio_df: pd.DataFrame)
    def calculate_stress_metrics(stress_params: Dict) -> Dict[str, Any]
    def generate_summary_insights(metrics: Dict) -> List[str]

def run_scenario_analysis(portfolio_df: pd.DataFrame, scenarios: Dict) -> Dict[str, Dict]
```

**Key Metrics Calculated**:
- Portfolio Value Under Stress
- Reserve Coverage Ratio
- Maximum Drawdown
- Time to Liquidity
- Volatility/Liquidity breach flags

#### `utils/report_generator.py`
**PDF report generation**

```python
class ReportGenerator:
    def generate_stress_test_report(metrics: Dict, insights: List[str]) -> bytes
    def generate_filename() -> str
    def save_report(pdf_buffer: bytes, filename: str) -> str
```

### Configuration

#### `utils/config.py`
**System configuration constants**

```python
# Application Settings
PAGE_TITLE = "Church Asset Risk Dashboard"
PAGE_ICON = "📊"

# Risk Parameters
ANNUAL_OPEX_SGD = 2_400_000  # 12-month operational expenses
RESERVE_MONTHS_REQUIRED = 12  # Reserve coverage requirement
VOLATILITY_BREACH_THRESHOLD = 0.20  # 20% decline threshold

# Stress Test Parameters
STRESS_PARAMS = {
    "interest_rate_shock": {"min": -0.02, "max": 0.02, "default": 0.0},
    "inflation_spike": {"min": 0.02, "max": 0.08, "default": 0.03},
    # ... other parameters
}

# Preset Scenarios
PRESET_SCENARIOS = {
    "Conservative": {"interest_rate_shock": -0.005, ...},
    "Moderate Stress": {"interest_rate_shock": -0.01, ...},
    # ... other scenarios
}
```

## 🚀 Deployment

### Local Development
```bash
# Start development server
source venv/bin/activate
streamlit run app.py
```

### Streamlit Community Cloud

#### Initial Deployment
1. **Push to GitHub**: Ensure all code committed to main branch
2. **Connect Streamlit Cloud**: Link GitHub repository
3. **Configure Deployment**:
   - **App Path**: `app.py`
   - **Python Version**: 3.8+
   - **Requirements**: `requirements.txt`
4. **Deploy**: Automatic deployment from main branch

#### Environment Configuration
- **No secrets required** for MVP (uses OpenBB Platform public data)
- **Portfolio data**: Committed as `portfolio.csv`
- **Market cache**: Auto-generated on first run

#### Production URL
- Format: `https://<app-name>.streamlit.app`
- **Custom domain**: Available with Streamlit Cloud Pro

### GitHub Actions Automation

#### Market Data Updates
**File**: `.github/workflows/market-data-update.yml`

**Schedule**: Weekdays 6 PM Singapore (10 AM UTC)
**Actions**: 
1. Fetch fresh market data via OpenBB Platform
2. Update asset-based storage files
3. Validate data quality
4. Commit changes to repository
5. Trigger Streamlit Cloud redeploy

#### Manual Triggers
```bash
# Standard full refresh (uses hybrid logic)
gh workflow run "Market Data Update" --field update_type=full_refresh

# Full refresh with custom start date
gh workflow run "Market Data Update" \
  --field update_type=full_refresh \
  --field start_date=2016-01-01

# Daily incremental update
gh workflow run "Market Data Update" --field update_type=incremental
```

**NEW: Command Line Usage**
```bash
# Test hybrid backfill locally
python scripts/update_market_data.py --type full_refresh --start-date 2016-01-01 --verbose

# Shows decision logic:
# "Historical data is X days old (>180), performing full refresh for data quality"
# OR 
# "Historical data is X days old (<180), using incremental backfill"
```

## 🧪 Testing

### System Validation
```bash
# Test data pipeline
python -c "
from utils.enhanced_data_sources import get_enhanced_data_manager
manager = get_enhanced_data_manager()
data = manager.fetch_market_data()
print('✅ Data pipeline working:', bool(data.get('singapore_rates')))
"

# Test dashboard components
python -c "
from app import load_portfolio_data, get_market_data
portfolio = load_portfolio_data()
market_data = get_market_data()
print('✅ Dashboard ready:', not portfolio.empty and bool(market_data))
"
```

### Data Quality Checks
```bash
# Verify market data freshness
python -c "
from utils.enhanced_data_sources import get_enhanced_data_manager
manager = get_enhanced_data_manager()
data = manager.fetch_market_data()
from datetime import datetime
last_updated = data.get('last_updated', '')
print(f'Last updated: {last_updated[:19]}')
"
```

## 🔧 Development Workflow

### Adding New Features

#### 1. Core Logic Implementation
```bash
# Add new functionality to appropriate utils/ module
# Example: New risk metric in utils/risk_engine.py
```

#### 2. UI Integration
```bash
# Add Streamlit components in app.py
# Follow existing patterns for parameter sliders and displays
```

#### 3. Testing
```bash
# Test with sample data
cp data/sample_portfolio.csv portfolio.csv
streamlit run app.py
```

#### 4. Documentation
```bash
# Update relevant documentation in docs/
# Add API documentation for new functions
```

### Market Data Integration

#### Adding New Assets
1. **Update Data Manager**: Add new asset type to `AssetDataManager`
2. **Enhance Data Sources**: Add fetching logic to `EnhancedDataSourceManager`
   - Add to `tickers` dictionary in `_fetch_market_indices_openbb()`
   - Add to `_get_mock_market_indices()` for fallback data
3. **Update UI**: Add display components in `app.py`
4. **Test Integration**: Verify end-to-end data flow with hybrid backfill logic

#### Modifying Data Sources
1. **OpenBB Integration**: Update ticker symbols or data providers
2. **Fallback Logic**: Ensure mock data includes new assets
3. **Validation**: Add quality checks for new data types
4. **Documentation**: Update architecture documentation

## 🐛 Troubleshooting

### Common Development Issues

#### Virtual Environment
```bash
# Module not found errors
source venv/bin/activate
pip install -r requirements.txt
```

#### OpenBB Platform
```bash
# Market data fetching issues
pip install --upgrade openbb
python -c "from openbb import obb; print('OpenBB version:', obb.__version__)"
```

#### Streamlit Issues
```bash
# Port conflicts
streamlit run app.py --server.port 8502

# Cache clearing
streamlit cache clear
```

### Production Monitoring

#### Data Pipeline Health
- **GitHub Actions**: Monitor workflow success/failure
- **Data Freshness**: Check `last_updated` timestamps
- **Error Logs**: Review GitHub Actions logs for issues

#### Dashboard Performance
- **Load Times**: Monitor Streamlit Cloud metrics
- **User Experience**: Test all dashboard features regularly
- **Error Handling**: Verify fallback mechanisms work

## 📋 Code Standards

### Python Style
- **PEP 8**: Standard Python formatting
- **Type Hints**: Use for public interfaces
- **Docstrings**: Document all classes and key functions
- **Error Handling**: Comprehensive try/catch with logging

### Documentation
- **Inline Comments**: Explain complex logic
- **Module Docstrings**: Describe module purpose and usage
- **README Updates**: Keep documentation current with code changes

## 🔗 Related Documentation

- [🏗️ Architecture](../architecture/) - Technical architecture details
- [📋 Project Management](../project-management/) - Implementation planning
- [🚀 Getting Started](../getting-started/) - Setup and user guides

---

*For specific implementation examples and code patterns, refer to the existing codebase in `utils/` modules.*