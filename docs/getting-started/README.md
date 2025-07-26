# 🚀 Getting Started

## Quick Navigation
- [← Back to Main Documentation](../)
- [User Guide](user_guide.md) - Complete user manual for Investment Committee
- [Installation Guide](#installation) - Setup instructions below

## Overview

This section contains everything you need to get the Church Asset Risk Dashboard running and accessible to Investment Committee members.

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Git (for repository management)
- Virtual environment support

### Step-by-Step Setup

#### 1. Environment Setup
```bash
# Clone repository (if needed)
git clone <repository-url>
cd stress_testing

# Create and activate virtual environment (REQUIRED)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Verify virtual environment is active
which python  # Should show path with /venv/
```

#### 2. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify OpenBB Platform installation
python -c "from openbb import obb; print('✅ OpenBB Platform ready')"
```

#### 3. Initial Data Setup
```bash
# Test market data fetching
python -c "from utils.enhanced_data_sources import get_enhanced_data_manager; print('✅ Data sources ready')"

# Use sample portfolio for testing
cp data/sample_portfolio.csv portfolio.csv
```

#### 4. Launch Dashboard
```bash
# Start Streamlit application
streamlit run app.py
```

The dashboard opens automatically at `http://localhost:8501`

## 🎯 Quick Start Checklist

- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Market data accessible (OpenBB Platform connected)
- [ ] Portfolio data loaded (`portfolio.csv` exists)
- [ ] Dashboard running (`streamlit run app.py`)

## 📖 User Resources

### For Investment Committee Members
- **[User Guide](user_guide.md)** - Complete guide to using the dashboard
- **Dashboard URL**: `http://localhost:8501` (local) or deployed URL
- **PDF Reports**: Generated within dashboard, downloadable for committee review

### For Technical Staff
- **Configuration**: See `../development/` section
- **Troubleshooting**: Check virtual environment and dependencies
- **Updates**: Market data refreshes automatically via GitHub Actions

## 🔧 Configuration

### Key Settings
Essential configurations in `utils/config.py`:
- `ANNUAL_OPEX_SGD`: Annual operational expenses (default: SGD 2.4M)
- `RESERVE_MONTHS_REQUIRED`: Required reserve coverage (default: 12 months)

### Portfolio Data
- **Location**: `portfolio.csv` in project root
- **Format**: Asset Type, Amount (SGD), Fund Name, Liquidity Period, Notes
- **Editing**: Direct CSV editing or use dashboard's portfolio editor

## 🆘 Troubleshooting

### Common Issues

#### Virtual Environment
```bash
# If Python modules not found:
source venv/bin/activate
pip install -r requirements.txt
```

#### OpenBB Platform
```bash
# If market data fails:
pip install --upgrade openbb
```

#### Port Conflicts
```bash
# If port 8501 busy:
streamlit run app.py --server.port 8502
```

### Getting Help
- **Technical Issues**: See `../development/` documentation
- **User Questions**: Refer to [User Guide](user_guide.md)
- **Project Status**: Check `../project-management/project-checkpoint.md`

## 🔗 Related Documentation

- [🏗️ Architecture](../architecture/) - Technical implementation details
- [📋 Project Management](../project-management/) - Project planning and status
- [🛠️ Development](../development/) - Developer resources

---

*Next: Read the [User Guide](user_guide.md) for complete dashboard usage instructions*