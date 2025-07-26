"""
Church Asset Risk & Stress Testing Dashboard
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os

# Import our custom modules
from utils.config import (
    PAGE_TITLE, PAGE_ICON, STRESS_PARAMS, PRESET_SCENARIOS,
    ANNUAL_OPEX_SGD, RESERVE_MONTHS_REQUIRED
)
from utils.risk_engine import RiskEngine, run_scenario_analysis
from utils.enhanced_data_sources import get_enhanced_data_manager
from utils.report_generator import ReportGenerator


# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f4e79;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f4e79;
    }
    .risk-flag {
        color: #d63031;
        font-weight: bold;
    }
    .success-flag {
        color: #00b894;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_portfolio_data():
    """Load portfolio data with caching"""
    try:
        df = pd.read_csv("portfolio.csv")
        return df
    except FileNotFoundError:
        st.error("Portfolio file not found. Please ensure portfolio.csv exists.")
        return pd.DataFrame()


@st.cache_data
def get_market_data():
    """Get market data with caching"""
    manager = get_enhanced_data_manager()
    return manager.fetch_market_data(force_refresh=False, incremental=True)


def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Church Asset Risk & Stress Testing Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    portfolio_df = load_portfolio_data()
    market_data = get_market_data()
    
    if portfolio_df.empty:
        st.stop()
    
    # Sidebar for parameters
    st.sidebar.header("🎛️ Stress Test Parameters")
    
    # Preset scenarios
    st.sidebar.subheader("Quick Scenarios")
    preset_choice = st.sidebar.selectbox(
        "Choose preset scenario:",
        ["Custom"] + list(PRESET_SCENARIOS.keys())
    )
    
    # Initialize parameters
    if preset_choice == "Custom":
        params = {key: config["default"] for key, config in STRESS_PARAMS.items()}
    else:
        params = PRESET_SCENARIOS[preset_choice].copy()
    
    # Parameter sliders
    st.sidebar.subheader("Adjust Parameters")
    
    user_params = {}
    for param_key, config in STRESS_PARAMS.items():
        if param_key == "interest_rate_shock":
            user_params[param_key] = st.sidebar.slider(
                "Interest Rate Shock (%)",
                min_value=config["min"] * 100,
                max_value=config["max"] * 100,
                value=params[param_key] * 100,
                step=0.1
            ) / 100
        elif param_key == "inflation_spike":
            user_params[param_key] = st.sidebar.slider(
                "Inflation Spike (%)",
                min_value=config["min"] * 100,
                max_value=config["max"] * 100,
                value=params[param_key] * 100,
                step=0.1
            ) / 100
        elif param_key == "multi_asset_drawdown":
            user_params[param_key] = st.sidebar.slider(
                "Multi-Asset Drawdown (%)",
                min_value=config["min"] * 100,
                max_value=config["max"] * 100,
                value=params[param_key] * 100,
                step=1.0
            ) / 100
        elif param_key == "redemption_freeze_days":
            user_params[param_key] = st.sidebar.slider(
                "Redemption Freeze (days)",
                min_value=int(config["min"]),
                max_value=int(config["max"]),
                value=int(params[param_key]),
                step=1
            )
        elif param_key == "early_withdrawal_penalty":
            user_params[param_key] = st.sidebar.slider(
                "Early Withdrawal Penalty (%)",
                min_value=config["min"] * 100,
                max_value=config["max"] * 100,
                value=params[param_key] * 100,
                step=0.1
            ) / 100
        elif param_key == "counterparty_risk":
            user_params[param_key] = st.sidebar.slider(
                "Counterparty Risk (%)",
                min_value=config["min"] * 100,
                max_value=config["max"] * 100,
                value=params[param_key] * 100,
                step=0.5
            ) / 100
    
    # Market data context
    st.sidebar.subheader("📊 Market Context")
    data_manager = get_enhanced_data_manager()
    
    # Enhanced data manager provides different context structure
    data_source = market_data.get('data_source', 'Enhanced Data Sources')
    last_updated = market_data.get('last_updated', datetime.now().isoformat())
    
    st.sidebar.write(f"**Data Source:** {data_source}")
    st.sidebar.write(f"**Last Updated:** {last_updated[:19]}")
    
    # Key rates display from enhanced structure
    st.sidebar.write("**Key Rates:**")
    singapore_rates = market_data.get('singapore_rates', {})
    if singapore_rates:
        st.sidebar.write(f"• SORA Rate: {singapore_rates.get('sora_rate', 0)*100:.2f}%")
        st.sidebar.write(f"• FD Average: {singapore_rates.get('fd_rates_average', 0)*100:.2f}%")
    
    # Market indices display
    market_indices = market_data.get('market_indices', {})
    if market_indices:
        st.sidebar.write("**Market Indices:**")
        for index_name, index_data in market_indices.items():
            if isinstance(index_data, dict) and 'current_price' in index_data:
                st.sidebar.write(f"• {index_name}: ${index_data['current_price']:.2f}")
    
    # Currency rates display
    currency_rates = market_data.get('currency_rates', {})
    if currency_rates:
        st.sidebar.write("**Currency:**")
        st.sidebar.write(f"• SGD/USD: {currency_rates.get('sgd_usd', 0):.4f}")
    
    # Run stress test
    risk_engine = RiskEngine(portfolio_df)
    metrics = risk_engine.calculate_stress_metrics(user_params)
    insights = risk_engine.generate_summary_insights(metrics)
    
    # Main dashboard
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Portfolio Value (Stressed)",
            value=f"SGD {metrics['stressed_portfolio_value']:,.0f}",
            delta=f"{-metrics['portfolio_decline_pct']*100:.1f}%"
        )
    
    with col2:
        status_color = "🔴" if metrics['reserve_coverage_ratio'] < 1.0 else "✅"
        st.metric(
            label="Reserve Coverage",
            value=f"{metrics['reserve_coverage_ratio']:.2f}x",
            delta=f"{status_color} vs 1.0x required"
        )
    
    with col3:
        liquidity_status = "🔴" if metrics['liquidity_breach_flag'] else "✅"
        st.metric(
            label="Time to Liquidity",
            value=f"{metrics['time_to_liquidity_days']:.0f} days",
            delta=f"{liquidity_status} vs 90 day target"
        )
    
    # Risk flags
    st.subheader("🚨 Risk Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if metrics['volatility_breach_flag']:
            st.error(f"🔴 VOLATILITY BREACH: {metrics['portfolio_decline_pct']*100:.1f}% decline exceeds 20% threshold")
        else:
            st.success(f"✅ Volatility within limits: {metrics['portfolio_decline_pct']*100:.1f}% decline")
    
    with col2:
        if metrics['liquidity_breach_flag']:
            st.error(f"🔴 LIQUIDITY CONCERN: {metrics['time_to_liquidity_days']:.0f} days exceeds 90-day target")
        else:
            st.success(f"✅ Adequate liquidity: {metrics['time_to_liquidity_days']:.0f} days to access funds")
    
    # Key insights
    st.subheader("💡 Key Insights")
    for insight in insights:
        if "🔴" in insight or "⚠️" in insight:
            st.error(insight)
        else:
            st.success(insight)
    
    # Charts section
    st.subheader("📈 Portfolio Analysis")
    
    # Create visualizations
    tab1, tab2, tab3 = st.tabs(["Portfolio Breakdown", "Risk Metrics", "Scenario Comparison"])
    
    with tab1:
        # Portfolio composition chart
        breakdown = metrics['asset_breakdown']
        
        labels = list(breakdown.keys())
        values = [breakdown[asset]['amount_sgd'] for asset in labels]
        
        fig_pie = px.pie(
            values=values,
            names=labels,
            title="Portfolio Composition (Post-Stress)",
            labels={'names': 'Asset Type', 'values': 'Amount (SGD)'}
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Detailed breakdown table
        st.subheader("Detailed Portfolio Breakdown")
        breakdown_df = pd.DataFrame([
            {
                'Asset Type': asset_type.replace('_', ' '),
                'Amount (SGD)': f"{data['amount_sgd']:,.0f}",
                'Percentage': f"{data['percentage']:.1f}%",
                'Number of Holdings': data['count']
            }
            for asset_type, data in breakdown.items()
        ])
        st.dataframe(breakdown_df, use_container_width=True)
    
    with tab2:
        # Risk metrics visualization
        risk_metrics = {
            'Maximum Drawdown': metrics['max_drawdown_pct'] * 100,
            'Reserve Coverage': metrics['reserve_coverage_ratio'] * 100,
            'Liquidity Time (Days)': metrics['time_to_liquidity_days']
        }
        
        # Gauge chart for risk metrics
        fig_metrics = make_subplots(
            rows=1, cols=3,
            subplot_titles=list(risk_metrics.keys()),
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Drawdown gauge
        fig_metrics.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=risk_metrics['Maximum Drawdown'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Max Drawdown (%)"},
                delta={'reference': 20},
                gauge={'axis': {'range': [None, 50]},
                       'bar': {'color': "red" if risk_metrics['Maximum Drawdown'] > 20 else "green"},
                       'steps': [{'range': [0, 20], 'color': "lightgray"},
                                {'range': [20, 50], 'color': "lightcoral"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 20}}
            ),
            row=1, col=1
        )
        
        # Reserve coverage gauge
        fig_metrics.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=risk_metrics['Reserve Coverage'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Reserve Coverage (%)"},
                delta={'reference': 100},
                gauge={'axis': {'range': [0, 200]},
                       'bar': {'color': "green" if risk_metrics['Reserve Coverage'] >= 100 else "red"},
                       'steps': [{'range': [0, 100], 'color': "lightcoral"},
                                {'range': [100, 200], 'color': "lightgray"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 100}}
            ),
            row=1, col=2
        )
        
        # Liquidity gauge
        fig_metrics.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=risk_metrics['Liquidity Time (Days)'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Liquidity Time (Days)"},
                delta={'reference': 90},
                gauge={'axis': {'range': [0, 180]},
                       'bar': {'color': "green" if risk_metrics['Liquidity Time (Days)'] <= 90 else "red"},
                       'steps': [{'range': [0, 90], 'color': "lightgray"},
                                {'range': [90, 180], 'color': "lightcoral"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}
            ),
            row=1, col=3
        )
        
        fig_metrics.update_layout(height=300)
        st.plotly_chart(fig_metrics, use_container_width=True)
    
    with tab3:
        # Scenario comparison
        st.write("Compare current parameters against preset scenarios:")
        
        # Run all preset scenarios
        all_scenarios = {"Current Custom": user_params}
        all_scenarios.update(PRESET_SCENARIOS)
        
        scenario_results = run_scenario_analysis(portfolio_df, all_scenarios)
        
        # Create comparison table
        comparison_data = []
        for scenario_name, result in scenario_results.items():
            comparison_data.append({
                'Scenario': scenario_name,
                'Portfolio Value': f"SGD {result['stressed_portfolio_value']:,.0f}",
                'Decline %': f"{result['portfolio_decline_pct']*100:.1f}%",
                'Reserve Coverage': f"{result['reserve_coverage_ratio']:.2f}x",
                'Liquidity Days': f"{result['time_to_liquidity_days']:.0f}",
                'Volatility Risk': "🔴" if result['volatility_breach_flag'] else "✅",
                'Liquidity Risk': "🔴" if result['liquidity_breach_flag'] else "✅"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Scenario comparison chart
        scenarios = list(scenario_results.keys())
        portfolio_values = [result['stressed_portfolio_value'] for result in scenario_results.values()]
        
        fig_comparison = px.bar(
            x=scenarios,
            y=portfolio_values,
            title="Portfolio Value Under Different Scenarios",
            labels={'x': 'Scenario', 'y': 'Portfolio Value (SGD)'}
        )
        fig_comparison.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Export section
    st.subheader("📋 Export Report")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Generate PDF Report", type="primary"):
            try:
                report_generator = ReportGenerator()
                pdf_buffer = report_generator.generate_stress_test_report(metrics, insights)
                filename = report_generator.generate_filename()
                
                st.download_button(
                    label="📥 Download Report",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf"
                )
                st.success("Report generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    with col2:
        st.info("Generate a comprehensive PDF report with all stress test results, insights, and recommendations for Investment Committee review.")
    
    # Portfolio editor
    with st.expander("📝 Edit Portfolio Data"):
        st.write("Current portfolio composition:")
        edited_df = st.data_editor(
            portfolio_df,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Changes"):
                try:
                    edited_df.to_csv("portfolio.csv", index=False)
                    st.success("Portfolio updated successfully! Please refresh to see changes.")
                except Exception as e:
                    st.error(f"Error saving portfolio: {str(e)}")
        
        with col2:
            csv_data = portfolio_df.to_csv(index=False)
            st.download_button(
                label="Download Portfolio CSV",
                data=csv_data,
                file_name="portfolio_backup.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()