# 🚀 Getting Started

## Quick Navigation
- [← Back to Main Documentation](../)
- [📦 Installation Guide](installation.md) - **COMPLETE setup instructions**
- [📖 User Guide](user_guide.md) - Dashboard usage for Investment Committee
- [📊 Financial Methodology](financial-methodology.md) - **COMPREHENSIVE risk framework for IC members**

## Overview

Get the Church Asset Risk Dashboard running for Investment Committee members. This section provides quick orientation and guides you to the appropriate detailed resources.

## ⚡ Quick Setup Overview
**For detailed installation, see [Installation Guide](installation.md)**

1. **Prerequisites**: Python 3.8+, virtual environment
2. **Install**: `pip install -r requirements.txt` 
3. **Setup**: `cp data/sample_portfolio.csv portfolio.csv`
4. **Run**: `streamlit run app.py`

Dashboard opens at: `http://localhost:8501`

## 🎯 Quick Start Checklist

- [ ] **[Complete installation](installation.md)** - Detailed setup guide with troubleshooting
- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Dependencies installed and verified
- [ ] Portfolio data loaded (`portfolio.csv` exists)
- [ ] Dashboard running and accessible

## 📖 Next Steps

### For Investment Committee Members
- **[Financial Methodology](financial-methodology.md)** - **ESSENTIAL**: Comprehensive risk framework, calculations, and assumptions
- **[User Guide](user_guide.md)** - Complete dashboard usage guide
- **Dashboard Features**: Interactive stress testing, scenario analysis, PDF reports
- **Training**: Contact technical team for hands-on demonstration

#### **🎯 IC Priority Reading**
- **[Financial Methodology](financial-methodology.md)** covers:
  - Risk metric definitions and calculations (Maximum Drawdown, Reserve Coverage, Liquidity)
  - Stress testing methodology and scenario calibration
  - Asset risk profiles and modeling assumptions
  - Business assumptions requiring IC validation (SGD 2.4M OPEX, 12-month reserves)
  - Historical performance analysis and benchmarking
  - Implementation guidelines for regular IC review

### For Technical Staff
- **[Installation Guide](installation.md)** - Complete setup, troubleshooting, and verification
- **Configuration**: Key settings in `utils/config.py` (OPEX assumptions, reserve requirements)
- **Updates**: Market data refreshes automatically via GitHub Actions
- **Support**: See `../development/` section for technical resources

## 🔧 Key Configuration Settings

Essential business parameters in `utils/config.py`:
- `ANNUAL_OPEX_SGD`: Annual operational expenses (default: SGD 2.4M) - **Requires IC validation**
- `RESERVE_MONTHS_REQUIRED`: Required reserve coverage (default: 12 months) - **Industry standard: 3-6 months**

### Portfolio Data Management
- **Location**: `portfolio.csv` in project root
- **Format**: Asset Type, Amount (SGD), Fund Name, Liquidity Period, Notes
- **Sample Available**: `data/sample_portfolio.csv` for testing

## 🔗 Related Documentation

- [📦 Installation Guide](installation.md) - **Complete technical setup**
- [🏗️ Architecture](../architecture/) - Technical implementation details
- [📋 Project Management](../project-management/) - Project planning and current status
- [🛠️ Development](../development/) - Developer resources and API reference

---

*Ready to install? See the [Installation Guide](installation.md) for complete setup instructions.*