#!/usr/bin/env python3

"""
Automated Market Data Update Script for Church Asset Risk Dashboard
Used by GitHub Actions and manual data refresh operations
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.enhanced_data_sources import EnhancedDataSourceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Ensure required directories and environment are set up"""
    logger.info("Setting up environment...")
    
    # Ensure data directories exist
    base_dir = project_root / "data" / "market_cache"
    required_dirs = ["rates", "indices", "currencies", "bonds", "metadata", "current"]
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {dir_path}")
    
    logger.info("Environment setup completed")


def update_market_data(update_type: str = "incremental", start_date: str = "2018-01-01") -> bool:
    """
    Update market data using enhanced data source manager
    
    Args:
        update_type: "incremental" or "full_refresh"
        start_date: Start date for full refresh (YYYY-MM-DD format)
    
    Returns:
        bool: True if update successful
    """
    logger.info(f"Starting {update_type} market data update...")
    
    try:
        # Initialize data manager
        data_manager = EnhancedDataSourceManager()
        
        # Set start date for full refresh
        if update_type == "full_refresh":
            logger.info(f"Setting backfill start date to: {start_date}")
            data_manager.set_backfill_start_date(start_date)
        
        # Determine update parameters
        if update_type == "full_refresh":
            force_refresh = True
            incremental = False
            logger.info("Performing full market data refresh from OpenBB Platform")
        else:
            force_refresh = False
            incremental = True
            logger.info("Performing incremental market data update")
        
        # Fetch market data
        market_data = data_manager.fetch_market_data(
            force_refresh=force_refresh,
            incremental=incremental
        )
        
        # Validate data quality
        validation_result = validate_market_data(market_data)
        
        if not validation_result['valid']:
            logger.error(f"Data validation failed: {validation_result['errors']}")
            return False
        
        # Log success metrics
        log_update_metrics(market_data, update_type)
        
        logger.info(f"{update_type} market data update completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Market data update failed: {e}")
        return False

def validate_market_data(data: dict) -> dict:
    """
    Validate the quality and completeness of market data
    
    Args:
        data: Market data dictionary
    
    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    errors = []
    
    # Check required data sections
    required_sections = ['singapore_rates', 'market_indices', 'currency_rates', 'bond_yields']
    
    for section in required_sections:
        if section not in data or not data[section]:
            errors.append(f"Missing or empty section: {section}")
    
    # Check Singapore rates
    if 'singapore_rates' in data:
        rates = data['singapore_rates']
        # Support both old and new field names
        required_rates = ['sora_rate']
        optional_rates = ['fd_rates_average', 'fixed_deposit_rate']
        
        for rate in required_rates:
            if rate not in rates:
                errors.append(f"Missing Singapore rate: {rate}")
            elif not isinstance(rates[rate], (int, float)) or rates[rate] <= 0:
                errors.append(f"Invalid Singapore rate value: {rate}={rates[rate]}")
        
        # Check that at least one FD rate field exists
        if not any(rate in rates for rate in optional_rates):
            errors.append(f"Missing fixed deposit rate (expected one of: {optional_rates})")
    
    # Check market indices
    if 'market_indices' in data:
        indices = data['market_indices']
        required_indices = ['STI', 'MSCI_World']
        
        for index in required_indices:
            if index not in indices:
                errors.append(f"Missing market index: {index}")
            elif 'current_price' not in indices[index]:
                errors.append(f"Missing current price for index: {index}")
            elif indices[index]['current_price'] <= 0:
                errors.append(f"Invalid price for index: {index}={indices[index]['current_price']}")
    
    # Check currency rates
    if 'currency_rates' in data:
        currency = data['currency_rates']
        if 'sgd_usd' not in currency or currency['sgd_usd'] <= 0:
            errors.append("Invalid or missing SGD/USD exchange rate")
    
    # Check data freshness
    if 'last_updated' in data:
        try:
            last_update = datetime.fromisoformat(data['last_updated'].replace('Z', '+00:00'))
            hours_old = (datetime.now() - last_update.replace(tzinfo=None)).total_seconds() / 3600
            
            if hours_old > 48:  # Data older than 48 hours
                errors.append(f"Data is stale: {hours_old:.1f} hours old")
        except ValueError:
            errors.append("Invalid last_updated timestamp format")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': []
    }

def log_update_metrics(data: dict, update_type: str):
    """Log key metrics from the update"""
    logger.info("=== Update Metrics ===")
    logger.info(f"Update Type: {update_type}")
    logger.info(f"Data Source: {data.get('data_source', 'Unknown')}")
    logger.info(f"Last Updated: {data.get('last_updated', 'Unknown')}")
    
    # Log Singapore rates
    if 'singapore_rates' in data:
        rates = data['singapore_rates']
        logger.info(f"SORA Rate: {rates.get('sora_rate', 0):.3%}")
        logger.info(f"FD Rate: {rates.get('fd_rates_average', 0):.3%}")
    
    # Log market indices
    if 'market_indices' in data:
        indices = data['market_indices']
        for index_name, index_data in indices.items():
            price = index_data.get('current_price', 0)
            logger.info(f"{index_name} Price: ${price:.2f}")
    
    # Log currency
    if 'currency_rates' in data:
        currency = data['currency_rates']
        sgd_usd = currency.get('sgd_usd', 0)
        logger.info(f"SGD/USD Rate: {sgd_usd:.4f}")
    
    logger.info("=====================")

def cleanup_old_data():
    """Clean up old data files to manage storage"""
    logger.info("Cleaning up old data files...")
    
    try:
        data_manager = EnhancedDataSourceManager()
        cleaned_count = data_manager.cleanup_old_data(days_to_keep=60)  # Keep 2 months
        logger.info(f"Cleaned up {cleaned_count} old files")
        
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Update market data for Church Asset Risk Dashboard")
    parser.add_argument(
        "--type", 
        choices=["incremental", "full_refresh"],
        default="incremental",
        help="Type of update to perform (default: incremental)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up old data files after update"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true", 
        help="Only validate existing data without fetching new data"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--start-date",
        default="2018-01-01",
        help="Start date for full refresh backfill (YYYY-MM-DD, default: 2018-01-01)"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🚀 Market Data Update Script Started")
    logger.info(f"Update Type: {args.type}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    # Setup environment
    setup_environment()
    
    # Validate existing data if requested
    if args.validate_only:
        logger.info("Validating existing market data...")
        try:
            data_manager = EnhancedDataSourceManager()
            current_data = data_manager.fetch_market_data(force_refresh=False, incremental=False)
            validation_result = validate_market_data(current_data)
            
            if validation_result['valid']:
                logger.info("✅ Existing data validation passed")
                return 0
            else:
                logger.error("❌ Existing data validation failed:")
                for error in validation_result['errors']:
                    logger.error(f"  - {error}")
                return 1
                
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 1
    
    # Perform data update
    start_date = args.start_date if hasattr(args, 'start_date') else '2018-01-01'
    logger.info(f"Using start date: {start_date}")
    
    # Validate start date format
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        logger.error(f"Invalid start date format: {start_date}. Expected YYYY-MM-DD")
        return 1
    
    success = update_market_data(args.type, start_date)
    
    # Cleanup if requested and update was successful
    if args.cleanup and success:
        cleanup_old_data()
    
    if success:
        logger.info("✅ Market data update completed successfully")
        return 0
    else:
        logger.error("❌ Market data update failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)