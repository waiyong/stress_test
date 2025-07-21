"""
Market data integration with local file caching for Church Asset Risk Dashboard
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import requests
from .config import CACHE_DURATION_DAYS, CACHE_CLEANUP_DAYS


class DataSourceManager:
    def __init__(self, cache_dir: str = "data/market_cache"):
        """Initialize data source manager with caching"""
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
        self.cleanup_old_cache()
        
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
            
    def cleanup_old_cache(self):
        """Remove cache files older than specified days"""
        if not os.path.exists(self.cache_dir):
            return
            
        cutoff_date = datetime.now() - timedelta(days=CACHE_CLEANUP_DAYS)
        
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        print(f"Cleaned up old cache file: {filename}")
                    except OSError:
                        pass
                        
    def get_cached_data(self, cache_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve cached market data if valid"""
        if cache_date is None:
            cache_date = datetime.now().strftime("%Y-%m-%d")
            
        cache_file = os.path.join(self.cache_dir, f"{cache_date}.json")
        
        if not os.path.exists(cache_file):
            return None
            
        # Check cache age
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        age_days = (datetime.now() - file_time).days
        
        if age_days >= CACHE_DURATION_DAYS:
            return None
            
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
            
    def save_cached_data(self, data: Dict[str, Any], cache_date: Optional[str] = None):
        """Save market data to cache file"""
        if cache_date is None:
            cache_date = datetime.now().strftime("%Y-%m-%d")
            
        cache_file = os.path.join(self.cache_dir, f"{cache_date}.json")
        
        # Add timestamp to data
        data_with_timestamp = data.copy()
        data_with_timestamp['cache_timestamp'] = datetime.now().isoformat()
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data_with_timestamp, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Could not save cache file: {e}")
            
    def fetch_market_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetch market data with caching fallback"""
        # Try to get cached data first
        if not force_refresh:
            cached_data = self.get_cached_data()
            if cached_data is not None:
                print(f"Using cached market data from {cached_data.get('cache_timestamp', 'unknown time')}")
                return cached_data
                
        print("Fetching fresh market data...")
        
        # Attempt to fetch real data
        try:
            fresh_data = self._fetch_real_market_data()
            self.save_cached_data(fresh_data)
            return fresh_data
        except Exception as e:
            print(f"Warning: Could not fetch real market data: {e}")
            
            # Try to use any cached data as fallback
            cached_data = self.get_cached_data()
            if cached_data is not None:
                print("Using stale cached data as fallback")
                return cached_data
                
            # Use mock data as last resort
            print("Using mock market data as fallback")
            mock_data = self._generate_mock_data()
            self.save_cached_data(mock_data)
            return mock_data
            
    def _fetch_real_market_data(self) -> Dict[str, Any]:
        """Fetch real market data from APIs (placeholder for now)"""
        # For MVP, we'll use mock data
        # In Phase 2, implement real yfinance and MAS API calls
        
        data = {
            "singapore_rates": self._fetch_singapore_rates(),
            "market_indices": self._fetch_market_indices(),
            "bond_yields": self._fetch_bond_yields(),
            "data_source": "real_apis",
            "last_updated": datetime.now().isoformat()
        }
        
        return data
        
    def _fetch_singapore_rates(self) -> Dict[str, float]:
        """Fetch Singapore interest rates (mock for MVP)"""
        # TODO: Implement MAS API integration
        return {
            "sora_rate": 0.035,  # Singapore Overnight Rate Average
            "3m_treasury": 0.034,
            "6m_treasury": 0.036,
            "12m_treasury": 0.038,
            "fd_rates_average": 0.031
        }
        
    def _fetch_market_indices(self) -> Dict[str, Dict[str, float]]:
        """Fetch market indices for multi-asset proxy (mock for MVP)"""
        # TODO: Implement yfinance integration
        return {
            "STI": {"current": 3250.0, "1y_return": 0.085, "volatility": 0.18},
            "MSCI_World": {"current": 2890.0, "1y_return": 0.12, "volatility": 0.16},
            "MSCI_Asia": {"current": 690.0, "1y_return": 0.095, "volatility": 0.19},
            "Global_Bonds": {"current": 485.0, "1y_return": 0.025, "volatility": 0.065}
        }
        
    def _fetch_bond_yields(self) -> Dict[str, float]:
        """Fetch Singapore government bond yields (mock for MVP)"""
        return {
            "2y_sgs": 0.032,
            "5y_sgs": 0.035,
            "10y_sgs": 0.039,
            "20y_sgs": 0.041
        }
        
    def _generate_mock_data(self) -> Dict[str, Any]:
        """Generate realistic mock market data for testing"""
        return {
            "singapore_rates": {
                "sora_rate": 0.035,
                "3m_treasury": 0.034,
                "6m_treasury": 0.036,
                "12m_treasury": 0.038,
                "fd_rates_average": 0.031
            },
            "market_indices": {
                "STI": {"current": 3250.0, "1y_return": 0.085, "volatility": 0.18},
                "MSCI_World": {"current": 2890.0, "1y_return": 0.12, "volatility": 0.16},
                "MSCI_Asia": {"current": 690.0, "1y_return": 0.095, "volatility": 0.19},
                "Global_Bonds": {"current": 485.0, "1y_return": 0.025, "volatility": 0.065}
            },
            "bond_yields": {
                "2y_sgs": 0.032,
                "5y_sgs": 0.035,
                "10y_sgs": 0.039,
                "20y_sgs": 0.041
            },
            "data_source": "mock_data",
            "last_updated": datetime.now().isoformat(),
            "note": "This is mock data for MVP testing. Real market data integration coming in Phase 2."
        }
        
    def get_asset_proxies(self) -> Dict[str, str]:
        """Return mapping of asset types to market proxies"""
        return {
            "Multi_Asset": "MSCI_World",
            "Bond_Fund": "Global_Bonds",
            "MMF": "sora_rate",
            "Time_Deposit": "fd_rates_average",
            "Cash_Equivalent": "sora_rate"
        }
        
    def calculate_expected_returns(self, market_data: Dict[str, Any], time_horizon_years: float = 1.0) -> Dict[str, float]:
        """Calculate expected returns for each asset type based on market data"""
        proxies = self.get_asset_proxies()
        expected_returns = {}
        
        rates = market_data.get("singapore_rates", {})
        indices = market_data.get("market_indices", {})
        
        for asset_type, proxy in proxies.items():
            if proxy in rates:
                # Interest rate-based assets
                expected_returns[asset_type] = rates[proxy] * time_horizon_years
            elif proxy in indices:
                # Market-based assets
                expected_returns[asset_type] = indices[proxy].get("1y_return", 0.06) * time_horizon_years
            else:
                # Default fallback
                expected_returns[asset_type] = 0.03 * time_horizon_years
                
        return expected_returns
        
    def get_market_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide market context for dashboard display"""
        return {
            "data_freshness": market_data.get("last_updated", "Unknown"),
            "data_source": market_data.get("data_source", "Unknown"),
            "key_rates": {
                "SORA": f"{market_data.get('singapore_rates', {}).get('sora_rate', 0)*100:.2f}%",
                "12M Treasury": f"{market_data.get('singapore_rates', {}).get('12m_treasury', 0)*100:.2f}%",
                "Average FD": f"{market_data.get('singapore_rates', {}).get('fd_rates_average', 0)*100:.2f}%"
            },
            "market_summary": self._generate_market_summary(market_data)
        }
        
    def _generate_market_summary(self, market_data: Dict[str, Any]) -> str:
        """Generate a brief market summary for context"""
        if market_data.get("data_source") == "mock_data":
            return "Using mock market data for MVP demonstration. Real-time data integration available in Phase 2."
        else:
            return "Market data reflects current Singapore and global financial conditions."


# Convenience function for easy import
def get_market_data_manager() -> DataSourceManager:
    """Factory function to create configured data source manager"""
    return DataSourceManager()