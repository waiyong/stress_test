"""
Core risk calculation engine for Church Asset Risk & Stress Testing Dashboard
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any
from .config import (
    ANNUAL_OPEX_SGD, 
    RESERVE_MONTHS_REQUIRED,
    VOLATILITY_BREACH_THRESHOLD,
    LIQUIDITY_BREACH_DAYS,
    ASSET_RISK_PROFILES
)


class RiskEngine:
    def __init__(self, portfolio_df: pd.DataFrame):
        """Initialize risk engine with portfolio data"""
        self.portfolio_df = portfolio_df.copy()
        self.total_portfolio_value = portfolio_df['Amount_SGD'].sum()
        
    def calculate_stress_metrics(self, stress_params: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate all risk metrics under stress scenarios
        
        Args:
            stress_params: Dictionary of stress parameters
            
        Returns:
            Dictionary containing all calculated risk metrics
        """
        # Apply stress factors to portfolio
        stressed_portfolio = self._apply_stress_factors(stress_params)
        
        # Calculate individual metrics
        portfolio_value_stressed = stressed_portfolio['Amount_SGD'].sum()
        reserve_coverage_ratio = self._calculate_reserve_coverage(portfolio_value_stressed)
        max_drawdown = self._calculate_max_drawdown(portfolio_value_stressed)
        time_to_liquidity = self._calculate_time_to_liquidity(stressed_portfolio, stress_params)
        volatility_breach = self._check_volatility_breach(max_drawdown)
        liquidity_breach = self._check_liquidity_breach(time_to_liquidity)
        
        # Asset allocation breakdown
        asset_breakdown = self._calculate_asset_breakdown(stressed_portfolio)
        
        return {
            "original_portfolio_value": self.total_portfolio_value,
            "stressed_portfolio_value": portfolio_value_stressed,
            "portfolio_decline_pct": (self.total_portfolio_value - portfolio_value_stressed) / self.total_portfolio_value,
            "reserve_coverage_ratio": reserve_coverage_ratio,
            "max_drawdown_pct": max_drawdown,
            "time_to_liquidity_days": time_to_liquidity,
            "volatility_breach_flag": volatility_breach,
            "liquidity_breach_flag": liquidity_breach,
            "annual_opex_requirement": ANNUAL_OPEX_SGD,
            "reserve_months_covered": reserve_coverage_ratio * RESERVE_MONTHS_REQUIRED,
            "asset_breakdown": asset_breakdown,
            "stressed_portfolio_df": stressed_portfolio,
            "stress_parameters": stress_params
        }
    
    def _apply_stress_factors(self, stress_params: Dict[str, float]) -> pd.DataFrame:
        """Apply stress factors to each asset in portfolio"""
        stressed_portfolio = self.portfolio_df.copy()
        
        for idx, row in stressed_portfolio.iterrows():
            asset_type = row['Asset_Type']
            original_amount = row['Amount_SGD']
            
            if asset_type not in ASSET_RISK_PROFILES:
                continue
                
            profile = ASSET_RISK_PROFILES[asset_type]
            stressed_amount = original_amount
            
            # Apply interest rate shock
            if asset_type in ['Time_Deposit', 'MMF', 'Cash_Equivalent']:
                interest_impact = stress_params.get('interest_rate_shock', 0) * profile['interest_rate_sensitivity']
                stressed_amount *= (1 + interest_impact)
            
            # Apply multi-asset fund drawdown
            if asset_type == 'Multi_Asset':
                drawdown = stress_params.get('multi_asset_drawdown', 0)
                stressed_amount *= (1 + drawdown)
            
            # Apply bond fund stress (interest rate and credit risk)
            if asset_type == 'Bond_Fund':
                # Bond funds affected by interest rate changes and some market stress
                rate_impact = stress_params.get('interest_rate_shock', 0) * profile['interest_rate_sensitivity'] * -1  # Inverse relationship
                market_stress = stress_params.get('multi_asset_drawdown', 0) * 0.3  # Bonds less affected than equity
                stressed_amount *= (1 + rate_impact + market_stress)
            
            # Note: Early withdrawal penalties are applied later based on actual liquidity needs
            
            # Apply counterparty risk
            counterparty_risk = stress_params.get('counterparty_risk', 0)
            if counterparty_risk > 0:
                stressed_amount *= (1 - counterparty_risk)
            
            stressed_portfolio.loc[idx, 'Amount_SGD'] = float(max(0, stressed_amount))  # Ensure non-negative and proper dtype
        
        # Apply early withdrawal penalties only when liquidity needs force early withdrawal
        stressed_portfolio = self._apply_early_withdrawal_penalties(stressed_portfolio, stress_params)
            
        return stressed_portfolio
    
    def _apply_early_withdrawal_penalties(self, stressed_portfolio: pd.DataFrame, stress_params: Dict[str, float]) -> pd.DataFrame:
        """
        Apply early withdrawal penalties only when liquidity needs force early withdrawal
        
        Logic:
        1. Calculate immediate liquidity needs (annual OPEX requirement)
        2. Determine available liquid assets (MMF, Cash, short-term assets)
        3. Only apply penalties to Time Deposits if liquidity gap exists
        """
        # Calculate annual liquidity requirement
        required_liquidity = ANNUAL_OPEX_SGD
        
        # Calculate available liquid assets (assets with liquidity <= 30 days)
        liquid_assets = stressed_portfolio[
            (stressed_portfolio['Asset_Type'].isin(['Cash_Equivalent', 'MMF'])) |
            (stressed_portfolio['Liquidity_Period_Days'] <= 30)
        ]
        available_liquidity = liquid_assets['Amount_SGD'].sum()
        
        # Calculate liquidity gap
        liquidity_gap = max(0, required_liquidity - available_liquidity)
        
        if liquidity_gap > 0:
            # We need to break some Time Deposits early
            penalty_rate = stress_params.get('early_withdrawal_penalty', 0)
            
            # Get Time Deposits that could be withdrawn early (sorted by liquidity period)
            time_deposits = stressed_portfolio[
                (stressed_portfolio['Asset_Type'] == 'Time_Deposit') &
                (stressed_portfolio['Liquidity_Period_Days'] > 30)
            ].copy()
            
            if len(time_deposits) > 0 and penalty_rate < 0:  # Only apply if penalty exists
                # Sort by liquidity period (break shorter-term deposits first)
                time_deposits = time_deposits.sort_values('Liquidity_Period_Days')
                
                remaining_gap = liquidity_gap
                
                for idx, row in time_deposits.iterrows():
                    if remaining_gap <= 0:
                        break
                        
                    deposit_amount = row['Amount_SGD']
                    early_withdrawal_amount = min(deposit_amount, remaining_gap)
                    
                    # Apply penalty only to the amount withdrawn early
                    penalty_amount = early_withdrawal_amount * abs(penalty_rate)
                    new_amount = deposit_amount - penalty_amount
                    
                    stressed_portfolio.loc[idx, 'Amount_SGD'] = float(max(0, new_amount))
                    remaining_gap -= early_withdrawal_amount
        
        return stressed_portfolio
    
    def _calculate_reserve_coverage(self, stressed_value: float) -> float:
        """Calculate reserve coverage ratio vs required OPEX"""
        return stressed_value / ANNUAL_OPEX_SGD
    
    def _calculate_max_drawdown(self, stressed_value: float) -> float:
        """Calculate maximum drawdown percentage"""
        return (self.total_portfolio_value - stressed_value) / self.total_portfolio_value
    
    def _calculate_time_to_liquidity(self, stressed_portfolio: pd.DataFrame, stress_params: Dict[str, float]) -> float:
        """Calculate weighted average time to access portfolio liquidity"""
        total_value = stressed_portfolio['Amount_SGD'].sum()
        if total_value == 0:
            return float('inf')
            
        weighted_liquidity_days = 0
        redemption_freeze = stress_params.get('redemption_freeze_days', 0)
        
        for _, row in stressed_portfolio.iterrows():
            weight = row['Amount_SGD'] / total_value
            base_liquidity = row['Liquidity_Period_Days']
            
            # Add redemption freeze for MMFs and funds
            if row['Asset_Type'] in ['MMF', 'Multi_Asset', 'Bond_Fund']:
                adjusted_liquidity = base_liquidity + redemption_freeze
            else:
                adjusted_liquidity = base_liquidity
                
            weighted_liquidity_days += weight * adjusted_liquidity
            
        return weighted_liquidity_days
    
    def _check_volatility_breach(self, max_drawdown: float) -> bool:
        """Check if portfolio decline exceeds volatility threshold"""
        return max_drawdown > VOLATILITY_BREACH_THRESHOLD
    
    def _check_liquidity_breach(self, time_to_liquidity: float) -> bool:
        """Check if liquidity access time exceeds threshold"""
        return time_to_liquidity > LIQUIDITY_BREACH_DAYS
    
    def _calculate_asset_breakdown(self, stressed_portfolio: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate asset allocation breakdown after stress"""
        total_value = stressed_portfolio['Amount_SGD'].sum()
        
        breakdown = {}
        for asset_type in stressed_portfolio['Asset_Type'].unique():
            asset_data = stressed_portfolio[stressed_portfolio['Asset_Type'] == asset_type]
            asset_total = asset_data['Amount_SGD'].sum()
            
            breakdown[asset_type] = {
                'amount_sgd': asset_total,
                'percentage': (asset_total / total_value * 100) if total_value > 0 else 0,
                'count': len(asset_data)
            }
            
        return breakdown
    
    def generate_summary_insights(self, metrics: Dict[str, Any]) -> list:
        """Generate actionable insights based on stress test results"""
        insights = []
        
        # Reserve adequacy insights
        if metrics['reserve_coverage_ratio'] < 1.0:
            shortfall_months = (1.0 - metrics['reserve_coverage_ratio']) * RESERVE_MONTHS_REQUIRED
            insights.append(f"⚠️ Reserve shortfall: {shortfall_months:.1f} months below requirement under stress")
        elif metrics['reserve_coverage_ratio'] > 1.5:
            excess_months = (metrics['reserve_coverage_ratio'] - 1.0) * RESERVE_MONTHS_REQUIRED
            insights.append(f"✅ Strong reserve position: {excess_months:.1f} months above requirement")
        
        # Volatility insights
        if metrics['volatility_breach_flag']:
            decline_pct = metrics['portfolio_decline_pct'] * 100
            insights.append(f"🔴 High volatility risk: {decline_pct:.1f}% portfolio decline exceeds {VOLATILITY_BREACH_THRESHOLD*100}% threshold")
        
        # Liquidity insights  
        if metrics['liquidity_breach_flag']:
            insights.append(f"🔴 Liquidity concern: {metrics['time_to_liquidity_days']:.0f} days to access funds exceeds {LIQUIDITY_BREACH_DAYS} day threshold")
        
        # Asset concentration insights
        for asset_type, breakdown in metrics['asset_breakdown'].items():
            if breakdown['percentage'] > 50:
                insights.append(f"📊 High concentration: {breakdown['percentage']:.1f}% in {asset_type}")
        
        # Positive insights
        if not metrics['volatility_breach_flag'] and not metrics['liquidity_breach_flag']:
            insights.append("✅ Portfolio demonstrates resilience under current stress scenario")
            
        return insights


def run_scenario_analysis(portfolio_df: pd.DataFrame, scenarios: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
    """Run multiple stress scenarios and compare results"""
    engine = RiskEngine(portfolio_df)
    results = {}
    
    for scenario_name, params in scenarios.items():
        results[scenario_name] = engine.calculate_stress_metrics(params)
        
    return results