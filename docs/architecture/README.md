# 🏗️ Technical Architecture

## Quick Navigation
- [← Back to Main Documentation](../)
- [📊 System Diagrams](system-diagrams.md) - **Visual architecture and data flow diagrams**
- [DataOps Implementation](dataops-implementation.md) - Asset-based storage system
- [OpenBB Integration](openbb-integration.md) - Real market data pipeline

## Overview

This section documents the technical architecture of the Church Asset Risk Dashboard, focusing on the enhanced DataOps implementation and real market data integration.

## 🏛️ System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                 Church Asset Risk Dashboard                  │
├─────────────────────────────────────────────────────────────┤
│                    Streamlit Frontend                       │
│          (app.py - Interactive Risk Dashboard)              │
├─────────────────────────────────────────────────────────────┤
│                     Core Engine                             │
│  RiskEngine │ ReportGenerator │ EnhancedDataSourceManager   │
├─────────────────────────────────────────────────────────────┤
│                   Data Layer                                │
│  AssetDataManager │ Asset-Based Storage │ Market Cache      │
├─────────────────────────────────────────────────────────────┤
│                External Integrations                        │
│     OpenBB Platform │ GitHub Actions │ PDF Generation      │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Evolution

**Phase 1 (MVP)**: Simple file-based data with mock market information
**Phase 2 (DataOps)**: Production-grade asset-based storage with real market data
**Phase 3 (Current)**: Integrated dashboard with automated operations

## 📊 Data Architecture

### Asset-Based Storage System
Replaces monolithic JSON files with modular, scalable structure:

```
data/market_cache/
├── rates/                      # Singapore interest rates
│   └── singapore_rates_{date}.json
├── indices/                    # Market indices
│   ├── STI_{date}.json
│   ├── MSCI_World_{date}.json
│   ├── MSCI_Asia_{date}.json
│   └── Global_Bonds_{date}.json
├── currencies/                 # Exchange rates
│   └── SGDUSD_{date}.json
├── bonds/                      # Government bond yields
│   └── singapore_bonds_{date}.json
├── current/                    # Hot cache (0.002s access)
│   ├── STI_current.json
│   ├── singapore_rates_current.json
│   └── [other current data files]
└── metadata/                   # System monitoring
    └── data_status.json
```

### Performance Improvements
- **Load Time**: 2+ seconds → 0.002 seconds (1000x improvement)
- **Memory Usage**: 90% reduction through selective loading
- **Maintainability**: Isolated asset updates and debugging

## 🔄 Data Pipeline

### Enhanced Data Source Manager
**File**: `utils/enhanced_data_sources.py`

**Key Features**:
- OpenBB Platform integration (100+ data providers)
- Intelligent refresh strategies (incremental vs full)
- Multi-layer fallback system (OpenBB → Cache → Mock)
- Comprehensive error handling and logging

### Update Strategies

#### Incremental Updates (Daily)
- Fetches only current prices and rates
- ~3 seconds execution time
- Updates current data hot cache
- Triggered weekdays at 6 PM Singapore time

#### Full Refresh (Weekly)
- Complete historical data recalculation
- ~30 seconds execution time  
- Updates all asset files with historical data
- Manual trigger via GitHub Actions

### Automated Operations
**File**: `.github/workflows/market-data-update.yml`

**Schedule**: Weekdays 6 PM Singapore (10 AM UTC)
**Actions**: Data fetch → Validation → Commit → Deploy
**Monitoring**: Automated status reports and error handling

## 🔧 Core Modules

### Risk Engine (`utils/risk_engine.py`)
Central calculation engine implementing:
- Portfolio Value Under Stress calculation
- Reserve Coverage Ratio (vs 12-month OPEX)
- Maximum Drawdown computation
- Time to Liquidity analysis
- Volatility and Liquidity breach flags

### Asset Data Manager (`utils/asset_data_manager.py`)
Storage management system providing:
- Asset-specific file operations
- Current data aggregation for dashboard
- Historical data access by asset type
- Automatic cleanup and maintenance

### Report Generator (`utils/report_generator.py`)
PDF report creation with:
- Executive summary with key risk metrics
- Detailed scenario parameters and assumptions
- Risk flags and breach notifications
- Timestamped naming: `CPC_StressTest_YYYY-MM-DD_HH-MM.pdf`

## 📈 Market Data Integration

### Data Sources
- **Primary**: OpenBB Platform (professional-grade financial data)
- **Coverage**: Singapore rates, global indices, currency rates
- **Historical**: 2020-present (5,591+ data points including COVID period)
- **Refresh**: Daily incremental + weekly full refresh

### Data Quality
- **Completeness**: 99.64% data coverage validation
- **Accuracy**: Real-time price integrity checks
- **Freshness**: Automatic staleness detection (<48 hours)
- **Reliability**: Multiple fallback mechanisms

## 🛡️ Production Features

### Reliability
- Multi-layer fallback system ensures always-available data
- Comprehensive error handling with graceful degradation
- Data validation and quality checks at multiple stages
- Automated monitoring and alerting via GitHub Actions

### Security
- No sensitive credentials in codebase
- Environment-based configuration management
- Local file storage with appropriate access controls
- No external dependencies for core dashboard functionality

### Scalability
- Asset-based architecture allows adding new data types
- Modular design supports feature extensions
- Efficient memory usage and fast load times
- Automated cleanup prevents storage bloat

## 📚 Documentation Sections

### [📊 System Diagrams](system-diagrams.md) - **START HERE**
**Visual architecture documentation** with comprehensive diagrams:
- High-level system architecture and component relationships
- Data flow diagrams for market data pipeline
- User journey flowcharts for Investment Committee workflow
- Component interaction diagrams and performance architecture
- Reliability and fallback mechanisms

### [DataOps Implementation](dataops-implementation.md)
Complete technical guide covering:
- Migration from legacy to asset-based storage
- Performance optimization strategies
- Testing and validation procedures
- Operational monitoring and maintenance

### [OpenBB Integration](openbb-integration.md)
Market data pipeline documentation:
- OpenBB Platform setup and configuration
- Data provider selection and fallback strategies
- API rate limiting and error handling
- Integration testing and validation

## 🔗 Related Documentation

- [🚀 Getting Started](../getting-started/) - Installation and setup
- [📋 Project Management](../project-management/) - Implementation timeline
- [🛠️ Development](../development/) - Developer resources

---

*For detailed implementation guides, see the specific architecture documents linked above.*