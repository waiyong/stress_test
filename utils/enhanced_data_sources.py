"""
Enhanced Data Source Manager that integrates OpenBB Platform with Asset-Based Storage
Combines real-time data fetching with maintainable, scalable storage
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
import logging

from .asset_data_manager import AssetDataManager
from .config import CACHE_DURATION_DAYS, CACHE_CLEANUP_DAYS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import OpenBB Platform
try:
    from openbb import obb
    OPENBB_AVAILABLE = True
except ImportError:
    logger.warning("OpenBB Platform not available. Run: pip install openbb")
    OPENBB_AVAILABLE = False


class EnhancedDataSourceManager:
    """Enhanced data source manager with OpenBB integration and asset-based storage"""
    
    def __init__(self, cache_dir: str = "data/market_cache"):
        """Initialize enhanced data source manager"""
        self.asset_manager = AssetDataManager(cache_dir)
        self.last_full_refresh = None
        self.refresh_threshold_hours = 24  # Force full refresh after 24 hours
        self.backfill_start_date = "2018-01-01"  # Default backfill start date
    
    def set_backfill_start_date(self, start_date: str):
        """Set the start date for full refresh backfill"""
        self.backfill_start_date = start_date
        logger.info(f"Backfill start date set to: {start_date}")
        
    def fetch_market_data(self, force_refresh: bool = False, incremental: bool = True) -> Dict[str, Any]:
        """
        Fetch market data with intelligent refresh strategy
        
        Args:
            force_refresh: Force fetch fresh data from APIs
            incremental: Use incremental updates vs full refresh
        """
        try:
            # Check if we need a full refresh
            need_full_refresh = force_refresh or self._should_full_refresh()
            
            if need_full_refresh:
                logger.info("Performing full market data refresh from OpenBB Platform")
                return self._fetch_full_market_data()
            elif incremental:
                logger.info("Performing incremental market data update")
                return self._fetch_incremental_updates()
            else:
                logger.info("Loading cached market data")
                return self.asset_manager.get_current_market_data()
                
        except Exception as e:
            logger.error(f"Market data fetch failed: {e}")
            # Fallback to cached data
            cached_data = self.asset_manager.get_current_market_data()
            if cached_data.get('singapore_rates'):  # Has some data
                logger.warning("Using cached data due to fetch failure")
                return cached_data
            else:
                logger.error("No cached data available, using fallback")
                return self._get_fallback_data()
    
    def _should_full_refresh(self) -> bool:
        """Determine if a full refresh is needed based on data age"""
        try:
            # Check metadata for last update time
            metadata_file = self.asset_manager.metadata_dir / "data_status.json"
            metadata = self.asset_manager._load_json(metadata_file)
            
            if not metadata or not metadata.get('last_full_update'):
                return True  # No previous update recorded
            
            last_update = datetime.fromisoformat(metadata['last_full_update'])
            hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
            
            return hours_since_update >= self.refresh_threshold_hours
            
        except Exception as e:
            logger.warning(f"Could not determine refresh status: {e}")
            return True  # Default to refresh if unclear
    
    def _fetch_full_market_data(self) -> Dict[str, Any]:
        """Fetch complete market data from OpenBB Platform and save to asset storage"""
        if not OPENBB_AVAILABLE:
            logger.warning("OpenBB not available, using cached data")
            return self.asset_manager.get_current_market_data()
        
        try:
            # Fetch each asset type
            singapore_rates = self._fetch_singapore_rates_openbb()
            currency_rates = self._fetch_currency_rates_openbb()
            bond_yields = self._fetch_bond_yields_openbb()
            
            # Fetch market indices with full historical data
            indices_data = self._fetch_market_indices_openbb()
            
            # Save to asset-based storage
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Save each asset type
            self.asset_manager.save_singapore_rates(singapore_rates, date_str)
            self.asset_manager.save_currency_data("SGDUSD", currency_rates, date_str)
            self.asset_manager.save_bond_data(bond_yields, date_str)
            
            # Save indices data
            for index_name, index_data in indices_data.items():
                self.asset_manager.save_index_data(index_name, index_data, date_str)
            
            # Update metadata
            self.asset_manager.update_metadata("full_update")
            self.last_full_refresh = datetime.now()
            
            # Return aggregated data for immediate use
            return self.asset_manager.get_current_market_data()
            
        except Exception as e:
            logger.error(f"Full data fetch failed: {e}")
            raise e
    
    def _fetch_incremental_updates(self) -> Dict[str, Any]:
        """Fetch only current prices and rates for incremental updates"""
        if not OPENBB_AVAILABLE:
            return self.asset_manager.get_current_market_data()
        
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            updated_assets = []
            
            # Update current prices for indices (lightweight)
            index_tickers = {
                "STI": "^STI",
                "MSCI_World": "URTH", 
                "MSCI_Asia": "AAXJ",
                "Global_Bonds": "AGG"
            }
            
            for index_name, ticker in index_tickers.items():
                try:
                    # Get just latest price (1 day of data)
                    hist_data = obb.equity.price.historical(
                        symbol=ticker,
                        start_date=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                        end_date=datetime.now().strftime("%Y-%m-%d")
                    )
                    
                    if hist_data and hasattr(hist_data, 'results') and len(hist_data.results) > 0:
                        latest_price = float(hist_data.results[-1].close)
                        
                        # Save incremental price update (without full historical data)
                        price_data = {"current_price": latest_price}
                        self.asset_manager.save_index_data(index_name, price_data, date_str)
                        updated_assets.append(index_name)
                        
                except Exception as e:
                    logger.warning(f"Could not update {index_name}: {e}")
            
            # Update currency rates (always fetch these as they're volatile)
            try:
                currency_rates = self._fetch_currency_rates_openbb()
                self.asset_manager.save_currency_data("SGDUSD", currency_rates, date_str)
                updated_assets.append("SGDUSD")
            except Exception as e:
                logger.warning(f"Could not update currency rates: {e}")
            
            # Update metadata
            self.asset_manager.update_metadata("incremental_update")
            
            logger.info(f"Incremental update completed for {len(updated_assets)} assets: {updated_assets}")
            
            # Return current aggregated data
            return self.asset_manager.get_current_market_data()
            
        except Exception as e:
            logger.error(f"Incremental update failed: {e}")
            return self.asset_manager.get_current_market_data()
    
    def _fetch_singapore_rates_openbb(self) -> Dict[str, float]:
        """Fetch Singapore interest rates from OpenBB Platform"""
        if not OPENBB_AVAILABLE:
            return self._get_mock_singapore_rates()
            
        try:
            rates = {}
            
            # Try multiple methods to get Singapore rates
            try:
                if hasattr(obb.economy, 'interest_rates'):
                    sg_rates = obb.economy.interest_rates(country="singapore")
                    if sg_rates and hasattr(sg_rates, 'results') and len(sg_rates.results) > 0:
                        results = sg_rates.results
                        if isinstance(results, list) and len(results) > 0:
                            latest_rate = results[-1]
                            if hasattr(latest_rate, 'value'):
                                rates["policy_rate"] = float(latest_rate.value) / 100
            except Exception as e:
                logger.debug(f"Could not fetch from economy.interest_rates: {e}")
            
            # Build final rates with fallbacks
            final_rates = {
                "sora_rate": rates.get("policy_rate", 0.0325),
                "3m_treasury": rates.get("3m_treasury", 0.0340),
                "6m_treasury": rates.get("6m_treasury", 0.0355), 
                "12m_treasury": rates.get("12m_treasury", 0.0370),
                "fd_rates_average": rates.get("12m_treasury", 0.0370) + 0.005
            }
            
            logger.info(f"Successfully compiled Singapore rates with {len(rates)} real data points")
            return final_rates
                
        except Exception as e:
            logger.warning(f"Failed to fetch Singapore rates: {e}")
            return self._get_mock_singapore_rates()
    
    def _get_mock_singapore_rates(self) -> Dict[str, float]:
        """Mock Singapore rates for fallback"""
        return {
            "sora_rate": 0.0325,
            "3m_treasury": 0.0340,
            "6m_treasury": 0.0355, 
            "12m_treasury": 0.0370,
            "fd_rates_average": 0.0375
        }
    
    def _fetch_currency_rates_openbb(self) -> Dict[str, float]:
        """Fetch SGD exchange rates from OpenBB Platform"""
        if not OPENBB_AVAILABLE:
            return self._get_mock_currency_rates()
            
        try:
            # Get recent SGD/USD rate
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            
            sgd_usd_data = obb.currency.price.historical(
                symbol="SGDUSD=X", 
                start_date=start_date, 
                end_date=end_date
            )
            
            if sgd_usd_data and hasattr(sgd_usd_data, 'results') and len(sgd_usd_data.results) > 0:
                latest_result = sgd_usd_data.results[-1]
                if hasattr(latest_result, 'close'):
                    sgd_usd_rate = float(latest_result.close)
                    logger.info(f"Successfully fetched SGD/USD rate: {sgd_usd_rate:.4f}")
                    return {
                        "sgd_usd": sgd_usd_rate,
                        "usd_sgd": 1.0 / sgd_usd_rate
                    }
            
            logger.warning("No currency data returned from OpenBB")
            return self._get_mock_currency_rates()
                
        except Exception as e:
            logger.warning(f"Failed to fetch currency rates: {e}")
            return self._get_mock_currency_rates()
    
    def _get_mock_currency_rates(self) -> Dict[str, float]:
        """Mock currency rates for fallback"""
        return {
            "sgd_usd": 0.7420,
            "usd_sgd": 1.3477
        }
    
    def _fetch_bond_yields_openbb(self) -> Dict[str, float]:
        """Fetch Singapore government bond yields from OpenBB Platform"""
        if not OPENBB_AVAILABLE:
            return self._get_mock_bond_yields()
            
        try:
            # Try to get Singapore government bond yields
            # Note: This may not be available directly, using mock for now
            logger.info("Using mock bond yields (OpenBB Singapore bonds not directly available)")
            return self._get_mock_bond_yields()
                
        except Exception as e:
            logger.warning(f"Failed to fetch bond yields: {e}")
            return self._get_mock_bond_yields()
    
    def _get_mock_bond_yields(self) -> Dict[str, float]:
        """Mock bond yields for fallback"""
        return {
            "2y_sgs": 0.032,
            "5y_sgs": 0.035,
            "10y_sgs": 0.039,
            "20y_sgs": 0.041
        }
    
    def _fetch_market_indices_openbb(self) -> Dict[str, Dict[str, Any]]:
        """Fetch market indices from OpenBB Platform with full historical data"""
        if not OPENBB_AVAILABLE:
            return self._get_mock_market_indices()
            
        try:
            start_date = self.backfill_start_date
            indices_data = {}
            
            tickers = {
                "STI": "^STI",
                "MSCI_World": "URTH", 
                "MSCI_Asia": "AAXJ",
                "Global_Bonds": "AGG"
            }
            
            for index_name, ticker in tickers.items():
                try:
                    hist_data = obb.equity.price.historical(
                        symbol=ticker,
                        start_date=start_date
                    )
                    
                    if hist_data and hasattr(hist_data, 'results'):
                        df = pd.DataFrame([vars(result) for result in hist_data.results])
                        
                        if not df.empty and 'close' in df.columns:
                            # Process the data similar to original implementation
                            df = df.sort_values('date')
                            df['date'] = pd.to_datetime(df['date'])
                            
                            dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
                            prices = df['close'].tolist()
                            returns = df['close'].pct_change().dropna().tolist()
                            volumes = df['volume'].tolist() if 'volume' in df.columns else []
                            
                            current_price = float(df['close'].iloc[-1])
                            computed_metrics = self._compute_metrics(df)
                            
                            indices_data[index_name] = {
                                "current_price": current_price,
                                "historical_data": {
                                    "dates": dates,
                                    "prices": prices,
                                    "returns": returns,
                                    "volumes": volumes,
                                    "total_days": len(dates)
                                },
                                "computed_metrics": computed_metrics,
                                "data_quality": {
                                    "start_date": dates[0] if dates else None,
                                    "end_date": dates[-1] if dates else None,
                                    "data_completeness": len(dates) / self._expected_trading_days() if dates else 0.0
                                }
                            }
                            
                            logger.info(f"Fetched {index_name}: {len(dates)} days, ${current_price:.2f}")
                            
                except Exception as e:
                    logger.warning(f"Failed to fetch {ticker}: {e}")
                    # Use mock data for this index
                    indices_data[index_name] = self._get_mock_index_data(index_name)
            
            return indices_data
            
        except Exception as e:
            logger.error(f"Failed to fetch market indices: {e}")
            return self._get_mock_market_indices()
    
    def _get_mock_market_indices(self) -> Dict[str, Dict[str, Any]]:
        """Mock market indices for fallback"""
        return {
            "STI": {"current_price": 4200.0, "computed_metrics": {"1y_return": 0.08}},
            "MSCI_World": {"current_price": 173.0, "computed_metrics": {"1y_return": 0.12}},
            "MSCI_Asia": {"current_price": 85.0, "computed_metrics": {"1y_return": 0.10}},
            "Global_Bonds": {"current_price": 98.0, "computed_metrics": {"1y_return": 0.03}}
        }
    
    def _get_mock_index_data(self, index_name: str) -> Dict[str, Any]:
        """Get mock data for specific index"""
        mock_data = self._get_mock_market_indices()
        return mock_data.get(index_name, {"current_price": 100.0, "computed_metrics": {"1y_return": 0.05}})
    
    def _compute_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Compute risk metrics from price data (simplified version)"""
        try:
            returns = df['close'].pct_change().dropna()
            current_price = float(df['close'].iloc[-1])
            
            # Basic metrics
            metrics = {
                "1y_return": (current_price - float(df['close'].iloc[0])) / float(df['close'].iloc[0]) if len(df) > 0 else 0.0,
                "1y_volatility": float(returns.std() * np.sqrt(252)) if len(returns) > 0 else 0.15,
                "max_drawdown": float((df['close'] / df['close'].cummax() - 1).min()) if len(df) > 0 else -0.20
            }
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Error computing metrics: {e}")
            return {"1y_return": 0.05, "1y_volatility": 0.15, "max_drawdown": -0.20}
    
    def _expected_trading_days(self) -> int:
        """Calculate expected trading days since backfill start date"""
        start_year = int(self.backfill_start_date.split('-')[0])
        return int((datetime.now() - datetime(start_year, 1, 1)).days * (252/365))
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Provide fallback data when all else fails"""
        return {
            "singapore_rates": self._get_mock_singapore_rates(),
            "market_indices": self._get_mock_market_indices(),
            "currency_rates": self._get_mock_currency_rates(),
            "bond_yields": self._get_mock_bond_yields(),
            "data_source": "fallback_data",
            "last_updated": datetime.now().isoformat(),
            "note": "Using fallback data - APIs and cache unavailable"
        }
    
    def get_asset_history(self, asset_type: str, asset_name: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get historical data for specific asset from asset storage"""
        return self.asset_manager.get_asset_history(asset_type, asset_name, days)
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data files"""
        return self.asset_manager.cleanup_old_files(days_to_keep)


# Factory function for easy import
def get_enhanced_data_manager() -> EnhancedDataSourceManager:
    """Factory function to create enhanced data source manager"""
    return EnhancedDataSourceManager()