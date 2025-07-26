# 📊 Church Asset Risk & Stress Testing Dashboard - Documentation

## 🧭 Quick Navigation

- 🚀 **[Getting Started](getting-started/)** - Installation, setup, and user guides
- 🏗️ **[Architecture](architecture/)** - Technical implementation and data pipeline details  
- 📋 **[Project Management](project-management/)** - Planning, progress tracking, and roadmap
- 🛠️ **[Development](development/)** - Developer resources and API reference

## 📖 Project Overview

Interactive stress testing dashboard for CPC's Investment Committee, providing real-time risk analysis with Singapore market data through OpenBB Platform integration.

### Key Features
- **Real Market Data**: Live Singapore rates, market indices, and currency data
- **Interactive Stress Testing**: Adjustable parameters for comprehensive scenario analysis
- **Automated Operations**: GitHub Actions pipeline with daily data updates
- **Professional Reporting**: Timestamped PDF reports for Investment Committee review
- **Asset-Based Architecture**: 1000x performance improvement with modular data storage

## 🏗️ System Architecture Overview

```
stress_testing/
├── app.py                          # Main Streamlit dashboard
├── portfolio.csv                   # Investment portfolio data
├── requirements.txt                # Python dependencies
├── utils/                          # Core modules
│   ├── enhanced_data_sources.py   # OpenBB Platform integration
│   ├── asset_data_manager.py      # Asset-based storage system
│   ├── risk_engine.py             # Stress testing calculations
│   ├── report_generator.py        # PDF report generation
│   └── config.py                  # Configuration constants
├── scripts/
│   └── update_market_data.py      # Automated data updates
├── .github/workflows/
│   └── market-data-update.yml     # GitHub Actions automation
├── data/market_cache/              # Asset-based market data storage
│   ├── rates/                     # Singapore interest rates
│   ├── indices/                   # Market indices (STI, MSCI, etc.)
│   ├── currencies/                # Exchange rates
│   ├── bonds/                     # Government bond yields
│   ├── current/                   # Hot cache for dashboard
│   └── metadata/                  # System status tracking
└── docs/                          # Documentation (this folder)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment activated: `source venv/bin/activate`

### Run the Dashboard
```bash
# Install dependencies
pip install -r requirements.txt

# Launch Streamlit app
streamlit run app.py
```

Dashboard available at: `http://localhost:8501`

## 📊 Current System Status

- ✅ **Phase 1**: MVP Complete (Streamlit UI, core calculations, PDF reports)
- ✅ **Phase 2**: DataOps Implementation (OpenBB Platform, asset-based storage, automation)
- 🔄 **Phase 3**: Production Deployment (dashboard integration, IC rollout)

### Real Market Data Integration
- **Singapore Rates**: SORA, FD rates, government bonds
- **Market Indices**: STI, MSCI World, MSCI Asia, Global Bonds
- **Currency Data**: Live SGD/USD exchange rates
- **Historical Coverage**: 2020-present (5,591+ data points including COVID period)

## 📚 Documentation Structure

Each section provides focused documentation with clear navigation:

### 🚀 [Getting Started](getting-started/)
Essential guides for new users and developers
- Installation & setup instructions
- User guide for Investment Committee members
- Environment configuration

### 🏗️ [Architecture](architecture/)
Technical implementation details
- DataOps implementation with asset-based storage
- OpenBB Platform integration for real market data
- Performance optimizations and reliability features

### 🔧 [Operations](operations/)
Operational procedures and troubleshooting
- Data management runbook with refresh scenarios
- Backfill procedures and API usage guidelines
- Troubleshooting common data issues

### 📋 [Project Management](project-management/)
Project planning and progress tracking
- Master project plan and roadmap
- Implementation checkpoints and status updates
- Phase completion tracking

### 🛠️ [Development](development/)
Resources for developers and maintainers
- API reference and code documentation
- Deployment procedures and best practices
- Development workflow and testing strategies

## 🎯 Key Risk Metrics

The dashboard calculates comprehensive risk metrics:

- **Portfolio Value Under Stress**: Real-time valuation with market shock factors
- **Reserve Coverage Ratio**: Stressed portfolio value vs 12-month OPEX requirement
- **Maximum Drawdown**: Worst-case portfolio decline analysis
- **Time to Liquidity**: Average days to access funds under stress conditions
- **Risk Breach Flags**: Automated alerts for volatility >20% or liquidity concerns

## 📈 Market Data Integration

### Data Sources
- **Primary**: OpenBB Platform (100+ financial data providers)
- **Fallback**: Asset-based cache with weekly refresh
- **Emergency**: Mock data for uninterrupted operation

### Update Schedule
- **Daily**: Incremental updates (current prices, weekdays 6 PM Singapore)
- **Weekly**: Full historical data refresh (manual trigger)
- **Real-time**: Currency rates and market indices

## 🛡️ Production Features

### Reliability
- Multi-layer fallback system (OpenBB → Cache → Mock data)
- Comprehensive error handling and logging
- Data validation and quality checks
- Automated monitoring via GitHub Actions

### Performance
- Asset-based storage: 0.002s load time (1000x improvement)
- Intelligent caching with incremental updates
- Memory-efficient data access patterns
- Hot cache for dashboard responsiveness

### Security
- No sensitive credentials in codebase
- Local CSV storage for portfolio data
- Environment-based configuration
- No external dependencies for core functionality

## 📞 Support & Development

### Development Resources
- `CLAUDE.md`: AI assistant development guidance
- Inline code documentation throughout modules
- Comprehensive testing scripts and validation

### Project Contact
Built for CPC Investment Committee • Technical implementation completed July 2025

---

## 🔗 Cross-References

- **Main Application**: `../app.py` - Streamlit dashboard entry point
- **Configuration**: `../utils/config.py` - System constants and parameters
- **Development Guide**: `../CLAUDE.md` - Detailed development instructions

*For technical issues or feature requests, refer to the specific documentation sections above or contact the development team.*