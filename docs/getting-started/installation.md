# 📦 Installation Guide

## Quick Navigation
- [← Back to Getting Started](README.md)
- [User Guide](user_guide.md) - Complete dashboard usage guide

## Prerequisites

Before installing the Church Asset Risk Dashboard, ensure you have:

- **Python 3.8+** (Check: `python3 --version`)
- **Git** for repository management
- **Terminal/Command Line** access
- **8GB+ RAM** recommended for data processing

## 🚀 Quick Installation

### 1. Repository Setup
```bash
# If cloning from repository
git clone <repository-url>
cd stress_testing

# If you already have the code
cd stress_testing
```

### 2. Virtual Environment (CRITICAL)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (REQUIRED FOR ALL OPERATIONS)
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Verify activation - you should see (venv) in your prompt
which python  # Should show path containing /venv/
```

**⚠️ Important**: Always activate the virtual environment before running any commands!

### 3. Dependencies Installation
```bash
# Install all required packages
pip install -r requirements.txt

# Verify OpenBB Platform installation
python -c "from openbb import obb; print('✅ OpenBB Platform ready')"
```

### 4. Initial Setup
```bash
# Create portfolio data (use sample for testing)
cp data/sample_portfolio.csv portfolio.csv

# Test market data connection
python -c "from utils.enhanced_data_sources import get_enhanced_data_manager; print('✅ Market data ready')"
```

### 5. Launch Dashboard
```bash
# Start the application
streamlit run app.py
```

Your dashboard will open automatically at: `http://localhost:8501`

## 🛠️ Detailed Installation

### System Requirements

#### Minimum Requirements
- **OS**: macOS, Linux, or Windows 10+
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM
- **Storage**: 1GB free space
- **Network**: Internet connection for market data

#### Recommended
- **Memory**: 8GB+ RAM for smooth operation
- **Storage**: 2GB+ for market data cache
- **Network**: Stable broadband for real-time updates

### Dependencies Overview

The dashboard requires these key packages (installed via `requirements.txt`):

```
streamlit>=1.28.0     # Web dashboard framework
pandas>=2.0.0         # Data manipulation
numpy>=1.24.0         # Numerical computing
plotly>=5.15.0        # Interactive charts
reportlab>=4.0.0      # PDF generation
openbb                # Market data platform
requests>=2.31.0      # HTTP requests
```

### Virtual Environment Setup

#### Why Virtual Environment?
- **Isolation**: Prevents conflicts with other Python projects
- **Reproducibility**: Ensures consistent package versions
- **Required**: The dashboard was developed and tested in virtual environment

#### Step-by-Step Setup
```bash
# Navigate to project directory
cd stress_testing

# Create virtual environment
python3 -m venv venv
# Creates: venv/ folder with isolated Python installation

# Activate virtual environment
source venv/bin/activate

# Verify activation
echo $VIRTUAL_ENV  # Should show path to venv folder
```

#### Virtual Environment Commands
```bash
# Activate (run this every time you start working)
source venv/bin/activate

# Deactivate (when done working)
deactivate

# Check if active (should show venv path)
which python
```

### Market Data Setup

#### OpenBB Platform Configuration
The dashboard uses OpenBB Platform for real financial data:

```bash
# Test OpenBB connection
python -c "
from openbb import obb
print('OpenBB Platform version:', obb.__version__)
print('✅ Connection successful')
"
```

#### Data Storage Initialization
First run creates the market data cache structure:

```
data/market_cache/
├── rates/           # Singapore interest rates
├── indices/         # Market indices (STI, MSCI, etc.)
├── currencies/      # Exchange rates
├── bonds/           # Government bonds
├── current/         # Hot cache for dashboard
└── metadata/        # System status
```

### Portfolio Data Setup

#### Using Sample Data
```bash
# Copy sample portfolio (recommended for testing)
cp data/sample_portfolio.csv portfolio.csv
```

#### Custom Portfolio Data
Create `portfolio.csv` with this format:
```csv
Asset_Type,Amount_SGD,Fund_Name,Liquidity_Period_Days,Notes
Time_Deposit,500000,DBS 12M FD,365,Fixed rate 2.8%
MMF,300000,Fullerton SGD MMF,1,Variable rate
Multi_Asset,200000,Nikko AM Global Multi-Asset,30,Mixed allocation
```

## ✅ Installation Verification

### Quick Health Check
```bash
# 1. Virtual environment active
echo $VIRTUAL_ENV  # Should show venv path

# 2. Dependencies installed
pip list | grep streamlit  # Should show streamlit version

# 3. Market data accessible
python -c "from utils.enhanced_data_sources import get_enhanced_data_manager; print('✅ Data sources ready')"

# 4. Portfolio data present
ls -la portfolio.csv  # Should show file exists

# 5. Dashboard starts
streamlit run app.py  # Should open browser at localhost:8501
```

### Complete System Test
```bash
# Run comprehensive test
python -c "
print('🧪 Testing Church Asset Risk Dashboard Installation')
print('=' * 60)

try:
    # Test 1: Imports
    from utils.enhanced_data_sources import get_enhanced_data_manager
    from utils.risk_engine import RiskEngine
    import pandas as pd
    import streamlit as st
    print('✅ All modules imported successfully')
    
    # Test 2: Portfolio data
    portfolio_df = pd.read_csv('portfolio.csv')
    print(f'✅ Portfolio loaded: {len(portfolio_df)} assets')
    
    # Test 3: Market data
    manager = get_enhanced_data_manager()
    market_data = manager.fetch_market_data()
    print(f'✅ Market data loaded: {len(market_data)} data types')
    
    # Test 4: Risk engine
    risk_engine = RiskEngine(portfolio_df)
    test_params = {'interest_rate_shock': 0.0, 'inflation_spike': 0.03}
    metrics = risk_engine.calculate_stress_metrics(test_params)
    print(f'✅ Risk calculations working: {len(metrics)} metrics')
    
    print('\\n🎉 Installation successful! Ready to run dashboard.')
    
except Exception as e:
    print(f'❌ Installation issue: {e}')
    print('Please check installation steps above.')
"
```

## 🐛 Troubleshooting

### Common Installation Issues

#### Python Version
```bash
# Check Python version
python3 --version  # Should be 3.8+

# If too old, install newer Python
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
# Windows: Download from python.org
```

#### Virtual Environment Issues
```bash
# If venv creation fails
python3 -m pip install --upgrade pip
python3 -m venv venv --clear

# If activation fails
chmod +x venv/bin/activate
source venv/bin/activate
```

#### Package Installation Errors
```bash
# If pip install fails
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir

# If OpenBB fails to install
pip install openbb --no-deps
pip install -r requirements.txt
```

#### Network/Firewall Issues
```bash
# If market data fetch fails
python -c "import requests; print(requests.get('https://httpbin.org/get').status_code)"
# Should print: 200

# If corporate firewall blocks
# Contact IT for OpenBB Platform whitelist: *.openbb.co
```

#### Permission Errors
```bash
# If file permission issues (macOS/Linux)
chmod -R 755 stress_testing/
chmod +x venv/bin/activate

# If Windows permission issues
# Run terminal as Administrator
```

### Getting Help

#### Check Installation Status
```bash
# Verify all components
source venv/bin/activate
python -c "
import sys; print('Python:', sys.version)
import streamlit; print('Streamlit:', streamlit.__version__)
import pandas; print('Pandas:', pandas.__version__)
from openbb import obb; print('OpenBB:', obb.__version__)
print('✅ All dependencies ready')
"
```

#### Support Resources
- **Documentation**: See other files in `docs/getting-started/`
- **Architecture**: Check `docs/architecture/` for technical details
- **Development**: See `docs/development/` for troubleshooting

## 🚀 Next Steps

After successful installation:

1. **Read User Guide**: [user_guide.md](user_guide.md) for complete dashboard usage
2. **Test Dashboard**: Run `streamlit run app.py` and explore features
3. **Customize Portfolio**: Edit `portfolio.csv` with actual investment data
4. **Generate Reports**: Test PDF report generation for IC meetings

## 🔗 Related Documentation

- [🚀 Getting Started Overview](README.md) - Return to getting started
- [📖 User Guide](user_guide.md) - Complete dashboard usage
- [🏗️ Architecture](../architecture/) - Technical implementation
- [🛠️ Development](../development/) - Developer resources

---

*Installation complete? Continue to the [User Guide](user_guide.md) to learn how to use the dashboard.*