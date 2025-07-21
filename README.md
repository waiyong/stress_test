# Church Asset Risk & Stress Testing Dashboard

A comprehensive stress testing dashboard for church investment portfolios, built with Streamlit and Python.

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Launch the Streamlit app
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📊 Features

- **Interactive Stress Testing**: Adjust parameters via sliders to simulate various risk scenarios
- **Preset Scenarios**: Quick access to standard stress tests (Conservative, Moderate, Severe Crisis, etc.)
- **Real-time Calculations**: Instant risk metric updates as you modify parameters
- **Comprehensive Reporting**: Generate timestamped PDF reports for committee review
- **Portfolio Management**: Edit portfolio composition directly in the app
- **Visual Analytics**: Interactive charts and gauges for risk visualization

## 🏗️ Architecture

```
stress_testing/
├── app.py                  # Main Streamlit application
├── portfolio.csv           # Current portfolio data
├── requirements.txt        # Python dependencies
├── utils/
│   ├── config.py          # Configuration constants
│   ├── risk_engine.py     # Core risk calculations
│   ├── data_sources.py    # Market data with caching
│   └── report_generator.py # PDF report creation
├── data/
│   ├── sample_portfolio.csv
│   └── market_cache/      # Cached market data
└── venv/                  # Virtual environment
```

## 💡 Key Risk Metrics

- **Portfolio Value Under Stress**: Simulated portfolio value after stress factors
- **Reserve Coverage Ratio**: Portfolio value vs 12-month operational expenses
- **Maximum Drawdown**: Worst-case portfolio decline percentage
- **Time to Liquidity**: Average days to access funds under stress
- **Risk Flags**: Volatility and liquidity breach warnings

## 🛠️ Development

### Adding New Stress Scenarios
Edit `utils/config.py` and add to `PRESET_SCENARIOS`:

```python
"New Scenario": {
    "interest_rate_shock": -0.01,
    "inflation_spike": 0.05,
    "multi_asset_drawdown": -0.20,
    # ... other parameters
}
```

### Modifying Risk Calculations
Core risk logic is in `utils/risk_engine.py`. The `RiskEngine` class handles all stress test calculations.

### Customizing Reports
PDF report templates are in `utils/report_generator.py`. Modify `ReportGenerator` class methods to change report formatting.

## 📈 Sample Portfolio

The app includes a realistic sample church portfolio with:
- SGD 3.4M total portfolio value
- Mix of Time Deposits (38%), MMFs (29%), Multi-Asset Funds (16%), Bonds (10%), Cash (6%)
- Conservative risk profile suitable for church treasury management

## 🔧 Configuration

Key settings in `utils/config.py`:
- `ANNUAL_OPEX_SGD`: Annual operational expenses (default: SGD 2.4M)
- `RESERVE_MONTHS_REQUIRED`: Required reserve coverage (default: 12 months)
- `VOLATILITY_BREACH_THRESHOLD`: Risk flag threshold (default: 20% decline)

## 📱 Deployment

For production deployment on Streamlit Community Cloud:

1. Push code to GitHub repository
2. Connect to Streamlit Community Cloud
3. Deploy from main branch
4. Access via custom `*.streamlit.app` URL

## 🛡️ Security

- Portfolio data is stored locally in CSV format
- No sensitive credentials required for MVP
- Market data cached locally (no external API dependencies in MVP)
- PDF reports generated client-side

## 📚 Documentation

- `CLAUDE.md`: Detailed development guidance for AI assistants
- `Project_plan.md`: Comprehensive project roadmap and architecture
- Inline code documentation throughout utils modules

## 🆘 Support

For technical issues or feature requests, refer to the project documentation or contact the development team.

---

*Built for CPC Investment Committee • Last Updated: July 2025*