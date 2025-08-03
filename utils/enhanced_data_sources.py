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

# Try to import OpenBB Platform with cloud deployment handling
try:
    from openbb import obb
    OPENBB_AVAILABLE = True
except (ImportError, PermissionError, OSError) as e:
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
        self.data_quality_threshold_days = 180  # Force full refresh if historical data >180 days old
    
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
            # Log OpenBB availability status
            if not OPENBB_AVAILABLE:
                logger.warning("OpenBB Platform not available - will use fallback data and ensure JSON files are created")
            
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
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Fallback to cached data
            try:
                cached_data = self.asset_manager.get_current_market_data()
                if cached_data.get('singapore_rates'):  # Has some data
                    logger.warning("Using cached data due to fetch failure")
                    return cached_data
                else:
                    logger.warning("No cached data available, generating fallback data and ensuring files are created")
                    fallback_data = self._get_fallback_data()
                    # Ensure fallback data is saved to create JSON files
                    self._save_fallback_data_to_files(fallback_data)
                    return fallback_data
            except Exception as fallback_error:
                logger.error(f"Even fallback data retrieval failed: {fallback_error}")
                logger.error(f"Fallback traceback: {traceback.format_exc()}")
                raise RuntimeError(f"Complete data fetch failure: original error: {e}, fallback error: {fallback_error}")
    
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

    def _get_existing_data_age_days(self) -> int:
        """Get age of existing historical dataset in days"""
        try:
            metadata_file = self.asset_manager.metadata_dir / "data_status.json"
            metadata = self.asset_manager._load_json(metadata_file)
            
            if not metadata or not metadata.get('last_full_update'):
                return float('inf')  # Never refreshed = infinite age
            
            last_refresh = datetime.fromisoformat(metadata['last_full_update'])
            return (datetime.now() - last_refresh).days
            
        except Exception as e:
            logger.warning(f"Could not determine data age: {e}")
            return float('inf')  # Default to infinite age if unclear
    
    def _get_existing_coverage(self, index_name: str) -> Optional[Dict[str, str]]:
        """Check existing data coverage for an index"""
        try:
            # Check current month file first
            current_file = self.asset_manager.indices_dir / f"{index_name}_{self.asset_manager.current_month}.json"
            data = self.asset_manager._load_json(current_file)
            
            if not data or not data.get('price_history'):
                return None
            
            # Get date range from price history
            dates = list(data['price_history'].keys())
            if not dates:
                return None
                
            return {
                'earliest_date': min(dates),
                'latest_date': max(dates),
                'data_points': len(dates)
            }
            
        except Exception as e:
            logger.debug(f"Could not determine existing coverage for {index_name}: {e}")
            return None
    
    def _fetch_full_market_data(self) -> Dict[str, Any]:
        """Fetch complete market data from OpenBB Platform and save to asset storage"""
        if not OPENBB_AVAILABLE:
            logger.warning("OpenBB not available, using cached data")
            return self.asset_manager.get_current_market_data()
        
        try:
            # Intelligent backfill decision
            data_age_days = self._get_existing_data_age_days()
            
            if data_age_days > self.data_quality_threshold_days:
                logger.info(f"Historical data is {data_age_days} days old (>{self.data_quality_threshold_days}), performing full refresh for data quality")
                use_full_refresh = True
            else:
                logger.info(f"Historical data is {data_age_days} days old (<{self.data_quality_threshold_days}), using incremental backfill")
                use_full_refresh = False
            
            # Fetch each asset type with historical data
            singapore_rates = self._fetch_singapore_rates_openbb(historical=True)
            currency_rates = self._fetch_currency_rates_openbb(historical=True)
            bond_yields = self._fetch_bond_yields_openbb(historical=True)
            
            # Fetch market indices with intelligent backfill
            indices_data = self._fetch_market_indices_openbb(force_full_refresh=use_full_refresh)
            
            # Save to asset-based storage
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Save each asset type
            self.asset_manager.save_singapore_rates(singapore_rates, date_str)
            self.asset_manager.save_currency_data("SGDUSD", currency_rates, date_str)
            self.asset_manager.save_bond_data(bond_yields, date_str)
            
            # Save indices data
            for index_name, index_data in indices_data.items():
                self.asset_manager.save_index_data(index_name, index_data, date_str)
            
            # Update metadata with appropriate refresh type
            refresh_type = "full_refresh" if use_full_refresh else "incremental_backfill"
            self.asset_manager.update_metadata(refresh_type)
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
    
    def _fetch_singapore_rates_openbb(self, historical: bool = False) -> Dict[str, Any]:
        """Fetch Singapore interest rates from OpenBB Platform with optional historical data"""
        if not OPENBB_AVAILABLE:
            return self._get_mock_singapore_rates(historical)
            
        try:
            if historical:
                # For historical data, generate realistic rate trends
                # Note: OpenBB may not have comprehensive Singapore rate history
                logger.info("Generating historical Singapore rates (OpenBB historical rates limited)")
                return self._get_mock_singapore_rates(historical)
            
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
            return self._get_mock_singapore_rates(historical)
    
    def _get_mock_singapore_rates(self, historical: bool = False) -> Dict[str, Any]:
        """Mock Singapore rates for fallback"""
        if historical:
            # Generate mock historical rate data
            from datetime import datetime, timedelta
            import numpy as np
            
            if hasattr(self, 'backfill_start_date'):
                start = datetime.strptime(self.backfill_start_date, '%Y-%m-%d')
            else:
                start = datetime.now() - timedelta(days=365)
            
            end = datetime.now()
            dates = pd.date_range(start=start, end=end, freq='D')
            dates_str = [d.strftime('%Y-%m-%d') for d in dates]
            
            # Generate realistic rate trends (Singapore raised rates during 2022-2024)
            n_days = len(dates_str)
            base_sora = 0.015  # Start lower
            trend = np.linspace(0, 0.017, n_days)  # Gradual increase
            noise = np.random.normal(0, 0.002, n_days)
            
            sora_rates = [max(0.01, min(0.04, base_sora + t + n)) for t, n in zip(trend, noise)]
            fd_rates = [rate + 0.008 for rate in sora_rates]  # FD typically higher
            treasury_3m = [rate + 0.003 for rate in sora_rates]
            treasury_6m = [rate + 0.005 for rate in sora_rates]
            treasury_12m = [rate + 0.007 for rate in sora_rates]
            
            current_rates = {
                "sora_rate": sora_rates[-1],
                "fixed_deposit_rate": fd_rates[-1],
                "1y_sgs": treasury_12m[-1],
                "10y_sgs": treasury_12m[-1] + 0.015
            }
            
            return {
                "current_rates": current_rates,
                "historical_data": {
                    "dates": dates_str,
                    "sora_rates": sora_rates,
                    "fd_rates": fd_rates,
                    "1y_sgs_rates": treasury_12m,
                    "10y_sgs_rates": [rate + 0.015 for rate in treasury_12m],
                    "total_days": len(dates_str)
                },
                "computed_metrics": self._compute_rates_metrics(sora_rates, fd_rates)
            }
        else:
            return {
                "sora_rate": 0.0325,
                "3m_treasury": 0.0340,
                "6m_treasury": 0.0355, 
                "12m_treasury": 0.0370,
                "fd_rates_average": 0.0375
            }
    
    def _compute_rates_metrics(self, sora_rates: list, fd_rates: list) -> Dict[str, float]:
        """Compute interest rate metrics"""
        try:
            sora_changes = np.diff(sora_rates)
            fd_changes = np.diff(fd_rates)
            
            return {
                "sora_volatility": float(np.std(sora_changes) * np.sqrt(252)),
                "fd_volatility": float(np.std(fd_changes) * np.sqrt(252)),
                "sora_1y_change": float(sora_rates[-1] - sora_rates[0]) if len(sora_rates) > 1 else 0.0,
                "fd_1y_change": float(fd_rates[-1] - fd_rates[0]) if len(fd_rates) > 1 else 0.0
            }
        except Exception as e:
            logger.warning(f"Failed to compute rates metrics: {e}")
            return {"sora_volatility": 0.008, "fd_volatility": 0.005}
    
    def _fetch_currency_rates_openbb(self, historical: bool = False) -> Dict[str, Any]:
        """Fetch SGD exchange rates from OpenBB Platform with optional historical data"""
        if not OPENBB_AVAILABLE:
            return self._get_mock_currency_rates(historical)
            
        try:
            if historical and hasattr(self, 'backfill_start_date'):
                # Fetch historical data for full refresh
                start_date = self.backfill_start_date
                end_date = datetime.now().strftime("%Y-%m-%d")
                logger.info(f"Fetching historical currency data from {start_date} to {end_date}")
            else:
                # Get recent SGD/USD rate only
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            
            sgd_usd_data = obb.currency.price.historical(
                symbol="SGDUSD=X", 
                start_date=start_date, 
                end_date=end_date
            )
            
            if sgd_usd_data and hasattr(sgd_usd_data, 'results') and len(sgd_usd_data.results) > 0:
                if historical and len(sgd_usd_data.results) > 1:
                    # Process historical data
                    df = pd.DataFrame([vars(result) for result in sgd_usd_data.results])
                    df = df.sort_values('date')
                    df['date'] = pd.to_datetime(df['date'])
                    
                    dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
                    sgd_usd_rates = df['close'].tolist()
                    usd_sgd_rates = (1.0 / df['close']).tolist()
                    
                    current_rate = float(df['close'].iloc[-1])
                    computed_metrics = self._compute_currency_metrics(df)
                    
                    return {
                        "current_rate": current_rate,
                        "historical_data": {
                            "dates": dates,
                            "sgd_usd_rates": sgd_usd_rates,
                            "usd_sgd_rates": usd_sgd_rates,
                            "total_days": len(dates)
                        },
                        "computed_metrics": computed_metrics
                    }
                else:
                    # Current rate only
                    latest_result = sgd_usd_data.results[-1]
                    if hasattr(latest_result, 'close'):
                        sgd_usd_rate = float(latest_result.close)
                        logger.info(f"Successfully fetched SGD/USD rate: {sgd_usd_rate:.4f}")
                        return {
                            "sgd_usd": sgd_usd_rate,
                            "usd_sgd": 1.0 / sgd_usd_rate
                        }
            
            logger.warning("No currency data returned from OpenBB")
            return self._get_mock_currency_rates(historical)
                
        except Exception as e:
            logger.warning(f"Failed to fetch currency rates: {e}")
            return self._get_mock_currency_rates(historical)
    
    def _get_mock_currency_rates(self, historical: bool = False) -> Dict[str, Any]:
        """Mock currency rates for fallback"""
        if historical:
            # Generate mock historical data
            from datetime import datetime, timedelta
            import numpy as np
            
            if hasattr(self, 'backfill_start_date'):
                start = datetime.strptime(self.backfill_start_date, '%Y-%m-%d')
            else:
                start = datetime.now() - timedelta(days=365)
            
            end = datetime.now()
            dates = pd.date_range(start=start, end=end, freq='D')
            dates_str = [d.strftime('%Y-%m-%d') for d in dates]
            
            # Generate realistic SGD/USD rates around 0.74
            base_rate = 0.7420
            rates = [base_rate + np.random.normal(0, 0.02) for _ in dates]
            rates = [max(0.70, min(0.78, rate)) for rate in rates]  # Bound rates
            
            return {
                "current_rate": rates[-1],
                "historical_data": {
                    "dates": dates_str,
                    "sgd_usd_rates": rates,
                    "usd_sgd_rates": [1.0/rate for rate in rates],
                    "total_days": len(dates_str)
                },
                "computed_metrics": {
                    "volatility": 0.08,
                    "1y_change": 0.02
                }
            }
        else:
            return {
                "sgd_usd": 0.7420,
                "usd_sgd": 1.3477
            }
    
    def _compute_currency_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Compute currency risk metrics from exchange rate data"""
        try:
            rates = df['close']
            returns = rates.pct_change().dropna()
            
            # Annualized volatility (252 trading days)
            volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0.0
            
            # Year-over-year change
            if len(rates) > 252:
                yoy_change = (rates.iloc[-1] - rates.iloc[-252]) / rates.iloc[-252]
            else:
                yoy_change = (rates.iloc[-1] - rates.iloc[0]) / rates.iloc[0]
            
            return {
                "volatility": float(volatility),
                "1y_change": float(yoy_change),
                "max_rate": float(rates.max()),
                "min_rate": float(rates.min())
            }
        except Exception as e:
            logger.warning(f"Failed to compute currency metrics: {e}")
            return {"volatility": 0.08, "1y_change": 0.02}
    
    def _fetch_bond_yields_openbb(self, historical: bool = False) -> Dict[str, Any]:
        """Fetch Singapore government bond yields from OpenBB Platform with optional historical data"""
        if not OPENBB_AVAILABLE:
            return self._get_mock_bond_yields(historical)
            
        try:
            # Try to get Singapore government bond yields
            # Note: OpenBB may not have direct Singapore bond yield data
            logger.info("Using mock bond yields (OpenBB Singapore bonds not directly available)")
            return self._get_mock_bond_yields(historical)
                
        except Exception as e:
            logger.warning(f"Failed to fetch bond yields: {e}")
            return self._get_mock_bond_yields(historical)
    
    def _get_mock_bond_yields(self, historical: bool = False) -> Dict[str, Any]:
        """Mock bond yields for fallback"""
        if historical:
            # Generate mock historical bond yield data
            from datetime import datetime, timedelta
            import numpy as np
            
            if hasattr(self, 'backfill_start_date'):
                start = datetime.strptime(self.backfill_start_date, '%Y-%m-%d')
            else:
                start = datetime.now() - timedelta(days=365)
            
            end = datetime.now()
            dates = pd.date_range(start=start, end=end, freq='D')
            dates_str = [d.strftime('%Y-%m-%d') for d in dates]
            
            # Generate realistic bond yield trends (yields rose 2022-2024)
            n_days = len(dates_str)
            base_2y = 0.025  # Start lower
            trend = np.linspace(0, 0.015, n_days)  # Gradual increase
            noise = np.random.normal(0, 0.003, n_days)
            
            yields_2y = [max(0.015, min(0.045, base_2y + t + n)) for t, n in zip(trend, noise)]
            yields_5y = [y + 0.005 for y in yields_2y]  # 5Y typically higher
            yields_10y = [y + 0.010 for y in yields_2y]  # 10Y even higher
            yields_20y = [y + 0.012 for y in yields_2y]  # 20Y highest
            
            current_yields = {
                "2y_sgs": yields_2y[-1],
                "5y_sgs": yields_5y[-1],
                "10y_sgs": yields_10y[-1],
                "20y_sgs": yields_20y[-1]
            }
            
            return {
                "current_yields": current_yields,
                "historical_data": {
                    "dates": dates_str,
                    "2y_yields": yields_2y,
                    "5y_yields": yields_5y,
                    "10y_yields": yields_10y,
                    "20y_yields": yields_20y,
                    "total_days": len(dates_str)
                },
                "computed_metrics": self._compute_bond_metrics(yields_2y, yields_10y)
            }
        else:
            return {
                "2y_sgs": 0.032,
                "5y_sgs": 0.035,
                "10y_sgs": 0.039,
                "20y_sgs": 0.041
            }
    
    def _compute_bond_metrics(self, yields_2y: list, yields_10y: list) -> Dict[str, float]:
        """Compute bond yield metrics"""
        try:
            changes_2y = np.diff(yields_2y)
            changes_10y = np.diff(yields_10y)
            
            # Yield curve spread (10Y - 2Y)
            spreads = [y10 - y2 for y2, y10 in zip(yields_2y, yields_10y)]
            
            return {
                "2y_volatility": float(np.std(changes_2y) * np.sqrt(252)),
                "10y_volatility": float(np.std(changes_10y) * np.sqrt(252)),
                "yield_curve_spread": float(spreads[-1]) if spreads else 0.007,
                "2y_1y_change": float(yields_2y[-1] - yields_2y[0]) if len(yields_2y) > 1 else 0.0,
                "10y_1y_change": float(yields_10y[-1] - yields_10y[0]) if len(yields_10y) > 1 else 0.0
            }
        except Exception as e:
            logger.warning(f"Failed to compute bond metrics: {e}")
            return {"2y_volatility": 0.005, "10y_volatility": 0.008, "yield_curve_spread": 0.007}
    
    def _fetch_market_indices_openbb(self, force_full_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Fetch market indices from OpenBB Platform with full historical data"""
        if not OPENBB_AVAILABLE:
            return self._get_mock_market_indices()
            
        try:
            indices_data = {}
            
            tickers = {
                "STI": "^STI",
                "MSCI_World": "URTH", 
                "MSCI_Asia": "AAXJ",
                "Global_Bonds": "AGG"
            }
            
            for index_name, ticker in tickers.items():
                try:
                    # Intelligent backfill: determine date range to fetch
                    if force_full_refresh:
                        # Full refresh: fetch complete history
                        start_date = self.backfill_start_date
                        logger.info(f"Full refresh for {index_name}: fetching from {start_date}")
                    else:
                        # Incremental backfill: check existing coverage and fetch gaps
                        existing_coverage = self._get_existing_coverage(index_name)
                        if existing_coverage and existing_coverage['earliest_date']:
                            existing_start = existing_coverage['earliest_date']
                            if self.backfill_start_date < existing_start:
                                # Fetch only the gap
                                start_date = self.backfill_start_date
                                end_date = existing_start
                                logger.info(f"Incremental backfill for {index_name}: fetching gap {start_date} to {end_date}")
                            else:
                                # No backfill needed, skip API call
                                logger.info(f"No backfill needed for {index_name}, existing coverage from {existing_start}")
                                continue
                        else:
                            # No existing data, fetch complete history
                            start_date = self.backfill_start_date
                            end_date = None
                            logger.info(f"No existing data for {index_name}: fetching from {start_date}")
                    
                    # Fetch historical data from API
                    if force_full_refresh or not existing_coverage:
                        hist_data = obb.equity.price.historical(
                            symbol=ticker,
                            start_date=start_date
                        )
                    else:
                        hist_data = obb.equity.price.historical(
                            symbol=ticker,
                            start_date=start_date,
                            end_date=end_date
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
    
    def _save_fallback_data_to_files(self, fallback_data: Dict[str, Any]):
        """Save fallback data to JSON files to ensure GitHub Actions creates files"""
        try:
            logger.info("Saving fallback data to ensure JSON files are created...")
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Save each component using the asset manager
            if 'singapore_rates' in fallback_data:
                self.asset_manager.save_singapore_rates(fallback_data['singapore_rates'], date_str)
                logger.info("✅ Saved fallback Singapore rates")
            
            if 'currency_rates' in fallback_data:
                self.asset_manager.save_currency_data("SGDUSD", fallback_data['currency_rates'], date_str)
                logger.info("✅ Saved fallback currency rates")
                
            if 'bond_yields' in fallback_data:
                self.asset_manager.save_bond_data(fallback_data['bond_yields'], date_str)
                logger.info("✅ Saved fallback bond yields")
            
            if 'market_indices' in fallback_data:
                for index_name, index_data in fallback_data['market_indices'].items():
                    self.asset_manager.save_index_data(index_name, index_data, date_str)
                    logger.info(f"✅ Saved fallback data for {index_name}")
            
            # Update metadata
            self.asset_manager.update_metadata("fallback_data_save")
            logger.info("✅ Fallback data successfully saved to JSON files")
            
        except Exception as e:
            logger.error(f"Failed to save fallback data to files: {e}")
            import traceback
            logger.error(f"Save fallback traceback: {traceback.format_exc()}")
            raise e
    
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