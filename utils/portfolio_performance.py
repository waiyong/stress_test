"""
Portfolio Performance Analysis Module
Calculates historical performance metrics for asset classes using market data proxies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Asset class to market data mapping
ASSET_PERFORMANCE_MAPPING = {
    "Time_Deposit": {
        "data_source": "singapore_rates",
        "field": "fd_rates",
        "description": "Fixed Deposit Rates"
    },
    "MMF": {
        "data_source": "singapore_rates", 
        "field": "sora_rates",
        "description": "Money Market (SORA)"
    },
    "Multi_Asset": {
        "data_source": "market_indices",
        "field": "msci_world",
        "description": "Multi-Asset (MSCI World)"
    },
    "Bond_Fund": {
        "data_source": "market_indices",
        "field": "singapore_bonds", 
        "description": "Singapore Bonds"
    },
    "Cash_Equivalent": {
        "data_source": "singapore_rates",
        "field": "sora_rates",
        "description": "Cash (SORA)"
    }
}


class PortfolioPerformanceAnalyzer:
    """Analyze historical performance of portfolio asset classes"""
    
    def __init__(self, market_data: Dict[str, Any]):
        """Initialize with market data from enhanced data manager"""
        self.market_data = market_data
        self.risk_free_rate = 0.025  # Default risk-free rate (2.5%)
        
        # Initialize asset data manager to access historical files
        from .asset_data_manager import AssetDataManager
        self.asset_manager = AssetDataManager("data/market_cache")
        
    def calculate_time_weighted_returns(self, prices: List[float], dates: List[str], 
                                      periods: List[str] = ["1Y", "3Y", "5Y", "ITD"]) -> Dict[str, float]:
        """Calculate time-weighted returns for different periods"""
        if not prices or not dates or len(prices) != len(dates):
            return {period: 0.0 for period in periods}
            
        try:
            df = pd.DataFrame({"date": pd.to_datetime(dates), "price": prices})
            df = df.sort_values("date")
            
            # Calculate returns for each period
            results = {}
            end_date = df["date"].iloc[-1]
            end_price = df["price"].iloc[-1]
            
            for period in periods:
                if period == "ITD":  # Inception to Date
                    start_price = df["price"].iloc[0]
                    start_date = df["date"].iloc[0]
                    years = (end_date - start_date).days / 365.25
                else:
                    # Parse period (1Y, 3Y, 5Y)
                    years = int(period[:-1])
                    start_date = end_date - timedelta(days=int(years * 365.25))
                    
                    # Find closest date
                    start_idx = df[df["date"] >= start_date].index
                    if len(start_idx) == 0:
                        results[period] = 0.0
                        continue
                    start_price = df.loc[start_idx[0], "price"]
                
                # Calculate annualized return
                if start_price > 0 and years > 0:
                    total_return = (end_price / start_price) - 1
                    annualized_return = (1 + total_return) ** (1 / years) - 1
                    results[period] = annualized_return
                else:
                    results[period] = 0.0
                    
            return results
            
        except Exception as e:
            logger.error(f"Error calculating returns: {e}")
            return {period: 0.0 for period in periods}
    
    def calculate_volatility(self, prices: List[float], annualized: bool = True) -> float:
        """Calculate volatility (standard deviation of returns)"""
        if len(prices) < 2:
            return 0.0
            
        try:
            price_series = pd.Series(prices)
            returns = price_series.pct_change().dropna()
            volatility = returns.std()
            
            if annualized:
                volatility *= np.sqrt(252)  # Annualize assuming 252 trading days
                
            return volatility
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.0
    
    def calculate_max_drawdown(self, prices: List[float]) -> float:
        """Calculate maximum drawdown from peak to trough"""
        if len(prices) < 2:
            return 0.0
            
        try:
            price_series = pd.Series(prices)
            cumulative = (1 + price_series.pct_change()).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return drawdown.min()
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    def calculate_sharpe_ratio(self, returns: float, volatility: float, 
                             risk_free_rate: Optional[float] = None) -> float:
        """Calculate Sharpe ratio (risk-adjusted return)"""
        if risk_free_rate is None:
            risk_free_rate = self.risk_free_rate
            
        if volatility == 0:
            return 0.0
            
        return (returns - risk_free_rate) / volatility
    
    def get_asset_class_data(self, asset_type: str) -> Tuple[List[float], List[str]]:
        """Extract historical data for specific asset class"""
        if asset_type not in ASSET_PERFORMANCE_MAPPING:
            logger.warning(f"Asset type {asset_type} not found in mapping")
            return [], []
            
        mapping = ASSET_PERFORMANCE_MAPPING[asset_type]
        data_source = mapping["data_source"]
        field = mapping["field"]
        
        try:
            import json
            from datetime import datetime
            
            # Read files directly from cache directory
            if data_source == "singapore_rates":
                # Read Singapore rates file
                current_month = datetime.now().strftime("%Y-%m")
                rates_file = f"data/market_cache/rates/singapore_rates_{current_month}.json"
                
                with open(rates_file, 'r') as f:
                    rates_data = json.load(f)
                
                if "historical_data" not in rates_data:
                    logger.warning("No historical_data in Singapore rates file")
                    return [], []
                    
                historical_data = rates_data["historical_data"]
                dates = historical_data.get("dates", [])
                
                if field == "fd_rates":
                    values = historical_data.get("fd_rates", [])
                elif field == "sora_rates":
                    values = historical_data.get("sora_rates", [])
                else:
                    values = []
                
                # Convert rates to cumulative returns
                if values and dates:
                    values = self._convert_rates_to_cumulative_returns(values, dates)
                    
            elif data_source == "market_indices":
                # Read market index files
                current_month = datetime.now().strftime("%Y-%m")
                
                if field == "msci_world":
                    index_file = f"data/market_cache/indices/MSCI_World_{current_month}.json"
                elif field == "singapore_bonds":
                    index_file = f"data/market_cache/indices/Global_Bonds_{current_month}.json"
                else:
                    logger.warning(f"Unknown market index field: {field}")
                    return [], []
                
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
                
                if "historical_data" not in index_data:
                    logger.warning(f"No historical_data in {index_file}")
                    return [], []
                    
                historical_data = index_data["historical_data"]
                dates = historical_data.get("dates", [])
                values = historical_data.get("prices", [])
            else:
                logger.warning(f"Unknown data source: {data_source}")
                return [], []
                
            return values, dates
            
        except Exception as e:
            logger.error(f"Error extracting data for {asset_type}: {e}")
            return [], []
    
    def _convert_rates_to_cumulative_returns(self, rates: List[float], dates: List[str]) -> List[float]:
        """Convert interest rates to cumulative return index"""
        if not rates or not dates:
            return []
            
        try:
            # Convert annual rates to daily returns, then cumulative
            daily_returns = [rate / 365 for rate in rates]
            cumulative = [1.0]  # Start with base value of 1
            
            for daily_return in daily_returns[1:]:
                cumulative.append(cumulative[-1] * (1 + daily_return))
                
            return cumulative
            
        except Exception as e:
            logger.error(f"Error converting rates to returns: {e}")
            return [1.0] * len(rates)
    
    def analyze_portfolio_performance(self, portfolio_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance for entire portfolio by asset class"""
        results = {}
        
        # Group portfolio by asset type
        asset_groups = portfolio_df.groupby('Asset_Type')['Amount_SGD'].sum()
        total_portfolio = asset_groups.sum()
        
        # Calculate performance for each asset class
        for asset_type, amount in asset_groups.items():
            weight = amount / total_portfolio
            prices, dates = self.get_asset_class_data(asset_type)
            
            if not prices or not dates:
                logger.warning(f"No data available for {asset_type}")
                continue
                
            # Calculate metrics
            returns = self.calculate_time_weighted_returns(prices, dates)
            volatility = self.calculate_volatility(prices)
            max_dd = self.calculate_max_drawdown(prices)
            
            # Calculate Sharpe ratios
            sharpe_ratios = {}
            for period, return_val in returns.items():
                sharpe_ratios[period] = self.calculate_sharpe_ratio(return_val, volatility)
            
            results[asset_type] = {
                "weight": weight,
                "amount_sgd": amount,
                "description": ASSET_PERFORMANCE_MAPPING[asset_type]["description"],
                "returns": returns,
                "volatility": volatility,
                "max_drawdown": max_dd,
                "sharpe_ratios": sharpe_ratios,
                "historical_prices": prices,  # Full historical data for timeline
                "historical_dates": dates
            }
        
        # Calculate portfolio-weighted performance
        portfolio_metrics = self._calculate_weighted_portfolio_metrics(results)
        
        return {
            "asset_classes": results,
            "portfolio_summary": portfolio_metrics,
            "analysis_date": datetime.now().isoformat(),
            "data_coverage": self._get_data_coverage()
        }
    
    def _calculate_weighted_portfolio_metrics(self, asset_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate portfolio-level metrics weighted by asset allocation"""
        if not asset_results:
            return {}
            
        periods = ["1Y", "3Y", "5Y", "ITD"]
        weighted_returns = {period: 0.0 for period in periods}
        weighted_volatility = 0.0
        weighted_max_dd = 0.0
        
        for asset_type, metrics in asset_results.items():
            weight = metrics["weight"]
            
            # Weighted returns
            for period in periods:
                weighted_returns[period] += weight * metrics["returns"].get(period, 0.0)
            
            # Weighted risk metrics (simplified - doesn't account for correlation)
            weighted_volatility += weight * metrics["volatility"]
            weighted_max_dd += weight * metrics["max_drawdown"]
        
        # Calculate portfolio Sharpe ratios
        sharpe_ratios = {}
        for period, return_val in weighted_returns.items():
            if weighted_volatility > 0:
                sharpe_ratios[period] = self.calculate_sharpe_ratio(return_val, weighted_volatility)
            else:
                sharpe_ratios[period] = 0.0
        
        return {
            "returns": weighted_returns,
            "volatility": weighted_volatility,
            "max_drawdown": weighted_max_dd,
            "sharpe_ratios": sharpe_ratios
        }
    
    def _get_data_coverage(self) -> Dict[str, str]:
        """Get information about data coverage periods"""
        try:
            # Check Singapore rates for date range
            rates_data = self.market_data.get("singapore_rates", {})
            historical = rates_data.get("historical_data", {})
            dates = historical.get("dates", [])
            
            if dates:
                return {
                    "start_date": dates[0],
                    "end_date": dates[-1],
                    "total_days": len(dates),
                    "years_covered": round(len(dates) / 365.25, 1)
                }
            else:
                return {"status": "No historical data available"}
                
        except Exception as e:
            logger.error(f"Error getting data coverage: {e}")
            return {"status": "Error retrieving data coverage"}


def create_performance_summary_table(performance_data: Dict[str, Any]) -> pd.DataFrame:
    """Create a summary table for display in Streamlit"""
    asset_data = performance_data.get("asset_classes", {})
    
    summary_rows = []
    for asset_type, metrics in asset_data.items():
        row = {
            "Asset Class": metrics["description"],
            "Allocation": f"{metrics['weight']*100:.1f}%",
            "Amount (SGD)": f"{metrics['amount_sgd']:,.0f}",
            "1Y Return": f"{metrics['returns'].get('1Y', 0)*100:.1f}%",
            "3Y Return": f"{metrics['returns'].get('3Y', 0)*100:.1f}%",
            "5Y Return": f"{metrics['returns'].get('5Y', 0)*100:.1f}%",
            "Volatility": f"{metrics['volatility']*100:.1f}%",
            "Max Drawdown": f"{metrics['max_drawdown']*100:.1f}%",
            "Sharpe (1Y)": f"{metrics['sharpe_ratios'].get('1Y', 0):.2f}"
        }
        summary_rows.append(row)
    
    return pd.DataFrame(summary_rows)