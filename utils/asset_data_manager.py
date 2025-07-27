"""
Enhanced Asset-Based Data Management System for Church Asset Risk Dashboard
Provides maintainable, scalable data operations with incremental updates
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
import logging
from pathlib import Path

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


class AssetDataManager:
    """Enhanced data manager with asset-based storage and incremental updates"""
    
    def __init__(self, base_cache_dir: str = "data/market_cache"):
        """Initialize asset-based data manager"""
        self.base_cache_dir = Path(base_cache_dir)
        self.current_month = datetime.now().strftime("%Y-%m")
        
        # Asset-specific subdirectories
        self.rates_dir = self.base_cache_dir / "rates"
        self.indices_dir = self.base_cache_dir / "indices" 
        self.currencies_dir = self.base_cache_dir / "currencies"
        self.bonds_dir = self.base_cache_dir / "bonds"
        self.metadata_dir = self.base_cache_dir / "metadata"
        self.current_dir = self.base_cache_dir / "current"
        
        self._ensure_directories()
        self._initialize_metadata()
    
    def _ensure_directories(self):
        """Ensure all asset directories exist"""
        for directory in [self.rates_dir, self.indices_dir, self.currencies_dir, 
                         self.bonds_dir, self.metadata_dir, self.current_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _initialize_metadata(self):
        """Initialize metadata tracking"""
        metadata_file = self.metadata_dir / "data_status.json"
        if not metadata_file.exists():
            initial_metadata = {
                "created": datetime.now().isoformat(),
                "last_full_update": None,
                "last_incremental_update": None,
                "data_version": "2.0",
                "assets_tracked": {
                    "rates": ["singapore_rates"],
                    "indices": ["STI", "MSCI_World", "MSCI_Asia", "Global_Bonds"],
                    "currencies": ["SGDUSD"],
                    "bonds": ["singapore_bonds"]
                }
            }
            self._save_json(metadata_file, initial_metadata)
    
    def _save_json(self, file_path: Path, data: Dict[str, Any]):
        """Save data to JSON file with error handling"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save {file_path}: {e}")
    
    def _load_json(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load data from JSON file with error handling"""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load {file_path}: {e}")
        return None
    
    def save_singapore_rates(self, rates_data: Dict[str, Any], date_str: Optional[str] = None) -> bool:
        """Save Singapore interest rates to asset-specific file"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        file_path = self.rates_dir / f"singapore_rates_{self.current_month}.json"
        
        # Load existing data or create new
        existing_data = self._load_json(file_path) or {"rates_history": {}, "metadata": {}}
        
        # Handle historical data structure vs simple rates
        if "current_rates" in rates_data and "historical_data" in rates_data:
            # New historical format
            existing_data["historical_data"] = rates_data["historical_data"]
            existing_data["computed_metrics"] = rates_data.get("computed_metrics", {})
            
            # Add current day to rates_history
            existing_data["rates_history"][date_str] = {
                **rates_data["current_rates"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Legacy simple rates format
            existing_data["rates_history"][date_str] = {
                **rates_data,
                "timestamp": datetime.now().isoformat()
            }
        
        # Update metadata
        existing_data["metadata"] = {
            "asset_type": "singapore_rates",
            "last_updated": datetime.now().isoformat(),
            "data_points": len(existing_data["rates_history"]),
            "has_historical": "historical_data" in existing_data,
            "date_range": {
                "start": min(existing_data["rates_history"].keys()),
                "end": max(existing_data["rates_history"].keys())
            }
        }
        
        self._save_json(file_path, existing_data)
        
        # Also save to current/ for quick access
        current_file = self.current_dir / "singapore_rates_current.json"
        current_rates = rates_data.get("current_rates", rates_data)
        current_data = {
            "rates": current_rates,
            "computed_metrics": rates_data.get("computed_metrics", {}),
            "last_updated": datetime.now().isoformat(),
            "source_file": f"singapore_rates_{self.current_month}.json"
        }
        self._save_json(current_file, current_data)
        
        logger.info(f"Saved Singapore rates for {date_str}")
        return True
    
    def save_index_data(self, index_name: str, price_data: Dict[str, Any], date_str: Optional[str] = None) -> bool:
        """Save market index data to asset-specific file"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        file_path = self.indices_dir / f"{index_name}_{self.current_month}.json"
        
        # Load existing data or create new
        existing_data = self._load_json(file_path) or {
            "price_history": {},
            "computed_metrics": {},
            "metadata": {}
        }
        
        # For incremental updates, we only add today's price data
        daily_data = {
            "price": price_data.get("current_price", 0.0),
            "timestamp": datetime.now().isoformat()
        }
        
        # If we have historical data, store it separately for analysis
        if "historical_data" in price_data:
            # Store comprehensive historical data (for full updates)
            existing_data["historical_data"] = price_data["historical_data"]
            existing_data["computed_metrics"] = price_data.get("computed_metrics", {})
            existing_data["data_quality"] = price_data.get("data_quality", {})
        
        # Add daily price point
        existing_data["price_history"][date_str] = daily_data
        
        # Update metadata
        existing_data["metadata"] = {
            "asset_type": "market_index",
            "index_name": index_name,
            "last_updated": datetime.now().isoformat(),
            "data_points": len(existing_data["price_history"]),
            "has_historical": "historical_data" in existing_data
        }
        
        self._save_json(file_path, existing_data)
        
        # Save to current/ for dashboard access
        current_file = self.current_dir / f"{index_name}_current.json"
        current_data = {
            "current_price": price_data.get("current_price", 0.0),
            "computed_metrics": price_data.get("computed_metrics", {}),
            "last_updated": datetime.now().isoformat(),
            "source_file": f"{index_name}_{self.current_month}.json"
        }
        self._save_json(current_file, current_data)
        
        logger.info(f"Saved {index_name} data for {date_str}")
        return True
    
    def save_currency_data(self, currency_pair: str, rate_data: Dict[str, Any], date_str: Optional[str] = None) -> bool:
        """Save currency exchange rates to asset-specific file"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        file_path = self.currencies_dir / f"{currency_pair}_{self.current_month}.json"
        
        # Load existing data or create new
        existing_data = self._load_json(file_path) or {"rates_history": {}, "metadata": {}}
        
        # Handle historical data structure vs simple rates
        if "current_rate" in rate_data and "historical_data" in rate_data:
            # New historical format
            existing_data["historical_data"] = rate_data["historical_data"]
            existing_data["computed_metrics"] = rate_data.get("computed_metrics", {})
            
            # Add current day to rates_history
            existing_data["rates_history"][date_str] = {
                "sgd_usd": rate_data["current_rate"],
                "usd_sgd": 1.0 / rate_data["current_rate"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Legacy simple rates format
            existing_data["rates_history"][date_str] = {
                **rate_data,
                "timestamp": datetime.now().isoformat()
            }
        
        # Update metadata
        existing_data["metadata"] = {
            "asset_type": "currency_rates",
            "currency_pair": currency_pair,
            "last_updated": datetime.now().isoformat(),
            "data_points": len(existing_data["rates_history"]),
            "has_historical": "historical_data" in existing_data
        }
        
        self._save_json(file_path, existing_data)
        
        # Save to current/
        current_file = self.current_dir / f"{currency_pair}_current.json"
        current_rates = {"sgd_usd": rate_data.get("current_rate", rate_data.get("sgd_usd", 0.74)), 
                        "usd_sgd": 1.0/rate_data.get("current_rate", rate_data.get("sgd_usd", 0.74))} if "current_rate" in rate_data else rate_data
        current_data = {
            "rates": current_rates,
            "computed_metrics": rate_data.get("computed_metrics", {}),
            "last_updated": datetime.now().isoformat(),
            "source_file": f"{currency_pair}_{self.current_month}.json"
        }
        self._save_json(current_file, current_data)
        
        logger.info(f"Saved {currency_pair} rates for {date_str}")
        return True
    
    def save_bond_data(self, bond_data: Dict[str, Any], date_str: Optional[str] = None) -> bool:
        """Save bond yield data to asset-specific file"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        file_path = self.bonds_dir / f"singapore_bonds_{self.current_month}.json"
        
        # Load existing data or create new
        existing_data = self._load_json(file_path) or {"yields_history": {}, "metadata": {}}
        
        # Handle historical data structure vs simple yields
        if "current_yields" in bond_data and "historical_data" in bond_data:
            # New historical format
            existing_data["historical_data"] = bond_data["historical_data"]
            existing_data["computed_metrics"] = bond_data.get("computed_metrics", {})
            
            # Add current day to yields_history
            existing_data["yields_history"][date_str] = {
                **bond_data["current_yields"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Legacy simple yields format
            existing_data["yields_history"][date_str] = {
                **bond_data,
                "timestamp": datetime.now().isoformat()
            }
        
        # Update metadata
        existing_data["metadata"] = {
            "asset_type": "bond_yields",
            "last_updated": datetime.now().isoformat(),
            "data_points": len(existing_data["yields_history"]),
            "has_historical": "historical_data" in existing_data
        }
        
        self._save_json(file_path, existing_data)
        
        # Save to current/
        current_file = self.current_dir / "singapore_bonds_current.json"
        current_yields = bond_data.get("current_yields", bond_data)
        current_data = {
            "yields": current_yields,
            "computed_metrics": bond_data.get("computed_metrics", {}),
            "last_updated": datetime.now().isoformat(),
            "source_file": f"singapore_bonds_{self.current_month}.json"
        }
        self._save_json(current_file, current_data)
        
        logger.info(f"Saved Singapore bond yields for {date_str}")
        return True
    
    def get_current_market_data(self) -> Dict[str, Any]:
        """Aggregate current data from all asset files for dashboard consumption"""
        try:
            # Load current data from each asset type
            singapore_rates = self._load_json(self.current_dir / "singapore_rates_current.json")
            sgd_currency = self._load_json(self.current_dir / "SGDUSD_current.json")
            singapore_bonds = self._load_json(self.current_dir / "singapore_bonds_current.json")
            
            # Load all index data
            indices_data = {}
            index_names = ["STI", "MSCI_World", "MSCI_Asia", "Global_Bonds"]
            
            for index_name in index_names:
                index_file = self.current_dir / f"{index_name}_current.json"
                index_data = self._load_json(index_file)
                if index_data:
                    indices_data[index_name] = index_data
            
            # Aggregate into dashboard format
            aggregated_data = {
                "singapore_rates": singapore_rates.get("rates", {}) if singapore_rates else {},
                "market_indices": {},
                "currency_rates": sgd_currency.get("rates", {}) if sgd_currency else {},
                "bond_yields": singapore_bonds.get("yields", {}) if singapore_bonds else {},
                "data_source": "openbb_platform_asset_based",
                "last_updated": datetime.now().isoformat(),
                "historical_period": "2020-present"
            }
            
            # Process indices data
            for index_name, index_data in indices_data.items():
                aggregated_data["market_indices"][index_name] = {
                    "current_price": index_data.get("current_price", 0.0),
                    "computed_metrics": index_data.get("computed_metrics", {})
                }
            
            # Add metadata about data freshness
            data_ages = []
            for asset_type in ["singapore_rates", "market_indices", "currency_rates", "bond_yields"]:
                if asset_type in aggregated_data and aggregated_data[asset_type]:
                    # This is simplified - in production you'd check each asset's timestamp
                    data_ages.append(0)  # Fresh data
            
            aggregated_data["data_freshness"] = {
                "oldest_data_hours": max(data_ages) if data_ages else 0,
                "all_data_fresh": all(age < 24 for age in data_ages),
                "assets_loaded": len([k for k in aggregated_data.keys() if aggregated_data[k] and k.endswith(('rates', 'indices', 'yields'))])
            }
            
            logger.info(f"Aggregated current market data from {len(indices_data)} indices + 3 other asset types")
            return aggregated_data
            
        except Exception as e:
            logger.error(f"Failed to aggregate current market data: {e}")
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Provide fallback data structure when asset files are unavailable"""
        return {
            "singapore_rates": {"sora_rate": 0.035, "fd_rates_average": 0.031},
            "market_indices": {
                "STI": {"current_price": 3250.0, "computed_metrics": {"1y_return": 0.08}}
            },
            "currency_rates": {"sgd_usd": 0.74, "usd_sgd": 1.35},
            "bond_yields": {"10y_sgs": 0.039},
            "data_source": "fallback_data",
            "last_updated": datetime.now().isoformat(),
            "note": "Using fallback data - asset files not available"
        }
    
    def get_asset_history(self, asset_type: str, asset_name: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get historical data for a specific asset"""
        try:
            if asset_type == "indices":
                file_path = self.indices_dir / f"{asset_name}_{self.current_month}.json"
            elif asset_type == "rates":
                file_path = self.rates_dir / f"singapore_rates_{self.current_month}.json"
            elif asset_type == "currencies":
                file_path = self.currencies_dir / f"{asset_name}_{self.current_month}.json"
            elif asset_type == "bonds":
                file_path = self.bonds_dir / f"singapore_bonds_{self.current_month}.json"
            else:
                logger.warning(f"Unknown asset type: {asset_type}")
                return None
            
            data = self._load_json(file_path)
            if not data:
                return None
            
            # Extract recent history based on days requested
            if asset_type == "indices" and "price_history" in data:
                history = data["price_history"]
                recent_dates = sorted(history.keys())[-days:]
                return {
                    "asset_name": asset_name,
                    "asset_type": asset_type,
                    "history": {date: history[date] for date in recent_dates},
                    "metadata": data.get("metadata", {})
                }
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get history for {asset_type}/{asset_name}: {e}")
            return None
    
    def update_metadata(self, update_type: str):
        """Update global metadata after data operations"""
        metadata_file = self.metadata_dir / "data_status.json"
        metadata = self._load_json(metadata_file) or {}
        
        if update_type == "full_update":
            metadata["last_full_update"] = datetime.now().isoformat()
        elif update_type == "incremental_update":
            metadata["last_incremental_update"] = datetime.now().isoformat()
        
        metadata["total_files"] = sum(len(list(d.glob("*.json"))) for d in [
            self.rates_dir, self.indices_dir, self.currencies_dir, self.bonds_dir
        ])
        
        self._save_json(metadata_file, metadata)
        logger.info(f"Updated metadata for {update_type}")
    
    def cleanup_old_files(self, days_to_keep: int = 90):
        """Clean up old monthly files to manage storage"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_month = cutoff_date.strftime("%Y-%m")
        
        cleaned_count = 0
        for directory in [self.rates_dir, self.indices_dir, self.currencies_dir, self.bonds_dir]:
            for file_path in directory.glob("*.json"):
                # Extract date from filename (assumes format: asset_YYYY-MM.json)
                try:
                    file_month = file_path.stem.split("_")[-1]
                    if file_month < cutoff_month:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.info(f"Cleaned up old file: {file_path.name}")
                except (IndexError, ValueError):
                    # Skip files that don't match expected naming pattern
                    continue
        
        logger.info(f"Cleaned up {cleaned_count} old files")
        return cleaned_count


# Factory function for easy import
def get_asset_data_manager() -> AssetDataManager:
    """Factory function to create configured asset data manager"""
    return AssetDataManager()