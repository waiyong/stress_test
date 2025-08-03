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
from utils.portfolio_performance import PortfolioPerformanceAnalyzer, create_performance_summary_table


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
        ["Custom"] + list(PRESET_SCENARIOS.keys()),
        help="Select a historical crisis scenario to test portfolio resilience against known market events"
    )
    
    # Initialize parameters
    if preset_choice == "Custom":
        params = {key: config["default"] for key, config in STRESS_PARAMS.items()}
    else:
        params = PRESET_SCENARIOS[preset_choice].copy()
    
    # Add scenario descriptions
    if preset_choice != "Custom":
        with st.sidebar.expander(f"ℹ️ About {preset_choice}"):
            if preset_choice == "Conservative":
                st.write("""
                **Parameters:**
                - Interest rates: -0.5% (mild policy easing)
                - Market decline: -15% (moderate correction)
                - Liquidity freeze: 5 days (minimal disruption)
                
                **What this tests:** Church resilience during normal economic slowdown
                **Historical context:** Similar to typical recession conditions
                **Use this for:** Annual planning baseline, routine stress testing
                """)
            elif preset_choice == "Moderate Stress":
                st.write("""
                **Parameters:**
                - Interest rates: -1.5% (significant policy response)
                - Market decline: -25% (substantial correction)
                - Liquidity freeze: 15 days (moderate market stress)
                
                **What this tests:** Church survival during significant economic stress
                **Historical context:** Similar to regional financial crises
                **Use this for:** Medium-term contingency planning
                """)
            elif preset_choice == "Severe Crisis":
                st.write("""
                **Parameters:**
                - Interest rates: -2% (emergency rate cuts)
                - Market decline: -40% (severe crash)
                - Liquidity freeze: 30 days (major banking disruption)
                - Bank failures: 5% (systemic risk)
                
                **What this tests:** Church survival during extreme financial crisis
                **Historical context:** Worse than most historical crises
                **Use this for:** Worst-case scenario planning, regulatory stress tests
                """)
            elif preset_choice == "2008 Financial Crisis":
                st.write("""
                **Parameters:**
                - Interest rates: -2% (emergency cuts to near zero)
                - Market decline: -37% (major banking crisis)
                - Liquidity freeze: 21 days (banking system stress)
                - Bank failures: 2% (selective institution failures)
                
                **What this tests:** Church survival during major financial crisis
                **Historical context:** Singapore STI fell 49% in 2008, global banking crisis
                **Use this for:** Conservative planning, understanding crisis impact
                """)
            elif preset_choice == "COVID-19 Scenario":
                st.write("""
                **Parameters:**
                - Interest rates: -1.5% (rapid policy response)
                - Market decline: -33% (sharp pandemic-driven drop)
                - Liquidity freeze: 14 days (temporary market disruption)
                - Low inflation: 2% (initial deflationary pressure)
                
                **What this tests:** Church resilience during pandemic-style shock
                **Historical context:** Singapore STI fell 34% in March 2020
                **Use this for:** Understanding modern crisis patterns, quick recovery scenarios
                """)
    else:
        with st.sidebar.expander("ℹ️ About Custom Parameters"):
            st.write("""
            **Custom Mode:** Adjust individual parameters to create your own scenario
            
            **Tips:**
            - Start with a preset, then modify specific parameters
            - Use extreme values to test portfolio limits
            - Consider parameter correlations (crises often have multiple effects)
            """)
    
    
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
                step=0.1,
                help="Central bank rate changes affect deposit and MMF returns. Negative = rate cuts (crisis response), Positive = rate hikes (inflation fighting)"
            ) / 100
        elif param_key == "inflation_spike":
            user_params[param_key] = st.sidebar.slider(
                "Inflation Spike (%)",
                min_value=config["min"] * 100,
                max_value=config["max"] * 100,
                value=params[param_key] * 100,
                step=0.1,
                help="Annual price increases affecting cost of operations. 3.5% = normal, 6-8% = high inflation crisis"
            ) / 100
        elif param_key == "multi_asset_drawdown":
            user_params[param_key] = st.sidebar.slider(
                "Multi-Asset Drawdown (%)",
                min_value=config["min"] * 100,
                max_value=config["max"] * 100,
                value=params[param_key] * 100,
                step=1.0,
                help="Stock and bond market decline severity. -20% = moderate crash, -40% = severe crisis (like 2008)"
            ) / 100
        elif param_key == "redemption_freeze_days":
            user_params[param_key] = st.sidebar.slider(
                "Redemption Freeze (days)",
                min_value=int(config["min"]),
                max_value=int(config["max"]),
                value=int(params[param_key]),
                step=1,
                help="Additional days funds are locked during crisis. 0 = normal operations, 30 = severe liquidity crisis"
            )
        elif param_key == "early_withdrawal_penalty":
            user_params[param_key] = st.sidebar.slider(
                "Early Withdrawal Penalty (%)",
                min_value=config["min"] * 100,
                max_value=config["max"] * 100,
                value=params[param_key] * 100,
                step=0.1,
                help="Cost of breaking fixed deposits early when cash is needed. -1% = typical penalty, -3% = crisis penalty"
            ) / 100
        elif param_key == "counterparty_risk":
            user_params[param_key] = st.sidebar.slider(
                "Counterparty Risk (%)",
                min_value=config["min"] * 100,
                max_value=config["max"] * 100,
                value=params[param_key] * 100,
                step=0.5,
                help="Risk of bank or fund manager failure. 0% = stable institutions, 5% = severe banking crisis"
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
            delta=f"{-metrics['portfolio_decline_pct']*100:.1f}%",
            help=f"Portfolio value after applying stress scenario. Original value: SGD {metrics['original_portfolio_value']:,.0f}"
        )
    
    with col2:
        status_color = "🔴" if metrics['reserve_coverage_ratio'] < 1.0 else "✅"
        months_covered = metrics['reserve_coverage_ratio'] * RESERVE_MONTHS_REQUIRED
        st.metric(
            label="Reserve Coverage",
            value=f"{metrics['reserve_coverage_ratio']:.2f}x",
            delta=f"{status_color} {months_covered:.1f} months covered",
            help=f"Shows how many months of operations (SGD {ANNUAL_OPEX_SGD/12:,.0f}/month) the stressed portfolio can fund"
        )
    
    with col3:
        liquidity_status = "🔴" if metrics['liquidity_breach_flag'] else "✅"
        st.metric(
            label="Time to Liquidity",
            value=f"{metrics['time_to_liquidity_days']:.0f} days",
            delta=f"{liquidity_status} vs 90 day target",
            help="Average time to access funds from the portfolio during this crisis scenario"
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
    tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Breakdown", "Risk Metrics", "Scenario Comparison", "Historical Performance"])
    
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
                mode="gauge+number",
                value=risk_metrics['Maximum Drawdown'],
                domain={'x': [0, 1], 'y': [0, 0.5]},
                title={'text': "Max Drawdown (%)", 'font': {'size': 16}},
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
                mode="gauge+number",
                value=risk_metrics['Reserve Coverage'],
                domain={'x': [0, 1], 'y': [0, 0.5]},
                title={'text': "Reserve Coverage (%)", 'font': {'size': 16}},
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
                mode="gauge+number",
                value=risk_metrics['Liquidity Time (Days)'],
                domain={'x': [0, 1], 'y': [0, 0.5]},
                title={'text': "Liquidity Time (Days)", 'font': {'size': 16}},
                gauge={'axis': {'range': [0, 180]},
                       'bar': {'color': "green" if risk_metrics['Liquidity Time (Days)'] <= 90 else "red"},
                       'steps': [{'range': [0, 90], 'color': "lightgray"},
                                {'range': [90, 180], 'color': "lightcoral"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}
            ),
            row=1, col=3
        )
        
        fig_metrics.update_layout(height=500)
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
    
    with tab4:
        # Historical Performance Analysis
        st.write("**Portfolio performance over time using market data proxies**")
        
        try:
            # Initialize performance analyzer
            performance_analyzer = PortfolioPerformanceAnalyzer(market_data)
            performance_results = performance_analyzer.analyze_portfolio_performance(portfolio_df)
            
            if performance_results and "asset_classes" in performance_results:
                # Performance Summary Table
                st.subheader("📊 Performance Summary")
                summary_table = create_performance_summary_table(performance_results)
                st.dataframe(summary_table, use_container_width=True)
                
                # Portfolio-level metrics
                portfolio_summary = performance_results.get("portfolio_summary", {})
                if portfolio_summary:
                    st.subheader("🎯 Portfolio-Level Performance")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        return_1y = portfolio_summary.get("returns", {}).get("1Y", 0)
                        st.metric("1-Year Return", f"{return_1y*100:.1f}%")
                    with col2:
                        return_3y = portfolio_summary.get("returns", {}).get("3Y", 0)
                        st.metric("3-Year Return", f"{return_3y*100:.1f}%")
                    with col3:
                        volatility = portfolio_summary.get("volatility", 0)
                        st.metric("Portfolio Volatility", f"{volatility*100:.1f}%")
                    with col4:
                        sharpe_1y = portfolio_summary.get("sharpe_ratios", {}).get("1Y", 0)
                        st.metric("Sharpe Ratio (1Y)", f"{sharpe_1y:.2f}")
                
                # Asset Class Performance Chart
                st.subheader("📈 Asset Class Returns Comparison")
                
                asset_data = performance_results["asset_classes"]
                chart_data = []
                for asset_type, metrics in asset_data.items():
                    chart_data.append({
                        "Asset Class": metrics["description"],
                        "1Y Return": metrics["returns"].get("1Y", 0) * 100,
                        "3Y Return": metrics["returns"].get("3Y", 0) * 100,
                        "5Y Return": metrics["returns"].get("5Y", 0) * 100,
                        "Volatility": metrics["volatility"] * 100
                    })
                
                chart_df = pd.DataFrame(chart_data)
                
                # Returns comparison bar chart
                fig_returns = px.bar(
                    chart_df.melt(id_vars=["Asset Class"], 
                                 value_vars=["1Y Return", "3Y Return", "5Y Return"],
                                 var_name="Period", value_name="Return (%)"),
                    x="Asset Class",
                    y="Return (%)",
                    color="Period",
                    title="Historical Returns by Asset Class (Annualized)",
                    barmode="group"
                )
                fig_returns.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_returns, use_container_width=True)
                
                # Add explanation for returns interpretation
                with st.expander("📊 Returns Analysis Explanation"):
                    st.write("""
                    **Why 5Y Returns May Be Lower Than 1Y Returns:**
                    
                    **Multi-Asset (MSCI World) Example:**
                    - **1Y Return (14.7%)**: Aug 2024 → Aug 2025 (recent bull market)
                    - **5Y Return (11.6%)**: Aug 2020 → Aug 2025 (includes COVID recovery)
                    
                    **This is normal because:**
                    1. **5Y period includes major crisis**: COVID-19 crash in March 2020
                    2. **Annualization smooths volatility**: 5Y return is compound annual growth rate
                    3. **Recent performance was strong**: 2024-2025 was exceptional for markets
                    4. **Base effect**: 5Y starts from higher base (post-COVID recovery)
                    
                    **For Investment Committee:**
                    - **1Y shows recent performance** (current market conditions)
                    - **5Y shows long-term resilience** (through full market cycle)
                    - **Both metrics are accurate** and professionally calculated
                    """)
                
                
                # Risk-Return Scatter Plot
                st.subheader("⚖️ Risk vs Return Analysis")
                
                fig_risk_return = px.scatter(
                    chart_df,
                    x="Volatility",
                    y="1Y Return",
                    size=[metrics["amount_sgd"] for metrics in asset_data.values()],
                    hover_name="Asset Class",
                    title="Risk vs Return (1-Year)",
                    labels={"Volatility": "Volatility (%)", "1Y Return": "1-Year Return (%)"}
                )
                fig_risk_return.add_hline(y=2.5, line_dash="dash", line_color="gray", 
                                        annotation_text="Risk-free rate (~2.5%)")
                fig_risk_return.update_traces(opacity=0.7)
                st.plotly_chart(fig_risk_return, use_container_width=True)
                
                # Time Series Chart for Portfolio Performance
                st.subheader("📅 Historical Performance Timeline")
                
                try:
                    # Let user choose which asset class timeline to display
                    timeline_options = {metrics["description"]: asset_type 
                                      for asset_type, metrics in asset_data.items() 
                                      if metrics["historical_prices"] and metrics["historical_dates"]}
                    
                    if timeline_options:
                        # Default to Multi-Asset if available, otherwise largest allocation
                        default_choice = None
                        if any("Multi-Asset" in desc for desc in timeline_options.keys()):
                            default_choice = [desc for desc in timeline_options.keys() if "Multi-Asset" in desc][0]
                        else:
                            largest_asset = max(asset_data.items(), key=lambda x: x[1]["amount_sgd"])
                            default_choice = largest_asset[1]["description"]
                        
                        selected_asset_desc = st.selectbox(
                            "Select asset class for timeline:",
                            options=list(timeline_options.keys()),
                            index=list(timeline_options.keys()).index(default_choice) if default_choice in timeline_options else 0,
                            help="Choose which asset class performance timeline to display"
                        )
                        
                        selected_asset_type = timeline_options[selected_asset_desc]
                        asset_metrics = asset_data[selected_asset_type]
                        
                        # Ensure we have valid data
                        if (asset_metrics["historical_prices"] and asset_metrics["historical_dates"] and 
                            len(asset_metrics["historical_prices"]) == len(asset_metrics["historical_dates"])):
                            
                            timeline_df = pd.DataFrame({
                                "Date": pd.to_datetime(asset_metrics["historical_dates"]),
                                "Performance Index": asset_metrics["historical_prices"]
                            })
                            
                            # Check for valid numeric data
                            timeline_df = timeline_df.dropna()
                            
                            if len(timeline_df) > 0:
                                # Normalize to start at 100 for easier interpretation
                                first_value = timeline_df["Performance Index"].iloc[0]
                                if first_value > 0:  # Avoid division by zero
                                    timeline_df["Performance Index"] = (timeline_df["Performance Index"] / first_value) * 100
                                
                                fig_timeline = px.line(
                                    timeline_df,
                                    x="Date",
                                    y="Performance Index",
                                    title=f"Performance Timeline - {selected_asset_desc}",
                                    labels={"Performance Index": "Performance Index (Base = 100)"}
                                )
                                
                                # Add key market events as annotations (only if dates are in range)
                                try:
                                    covid_date = pd.to_datetime("2020-03-23")
                                    bear_date = pd.to_datetime("2022-10-12")
                                    
                                    timeline_start = timeline_df["Date"].min()
                                    timeline_end = timeline_df["Date"].max()
                                    
                                    if timeline_start <= covid_date <= timeline_end:
                                        fig_timeline.add_vline(x=covid_date, line_dash="dash", line_color="red", 
                                                             annotation_text="COVID-19 Low")
                                                             
                                    if timeline_start <= bear_date <= timeline_end:
                                        fig_timeline.add_vline(x=bear_date, line_dash="dash", line_color="orange", 
                                                             annotation_text="2022 Bear Market")
                                except Exception:
                                    # If annotations fail, just skip them
                                    pass
                                
                                st.plotly_chart(fig_timeline, use_container_width=True)
                                
                                # Add context explanation
                                with st.expander("💡 Timeline Interpretation"):
                                    st.write(f"""
                                    **{selected_asset_desc} Historical Context:**
                                    
                                    **Performance Index Base = 100** (Starting value normalized to 100 for easy comparison)
                                    
                                    **Key Insights:**
                                    - **March 2020**: COVID-19 pandemic caused global market crash
                                    - **2020-2021**: Massive recovery driven by stimulus and vaccine development  
                                    - **2022**: Bear market due to inflation concerns and interest rate hikes
                                    - **2023-2025**: Recent recovery and growth period
                                    
                                    **For Investment Committee:**
                                    - Shows portfolio resilience through major crises
                                    - Demonstrates recovery patterns for long-term planning
                                    - Helps contextualize current stress test scenarios
                                    """)
                            else:
                                st.warning("No valid timeline data available after processing.")
                        else:
                            st.warning("Invalid or mismatched historical data for timeline display.")
                    else:
                        st.warning("No historical timeline data available for any asset class.")
                        
                except Exception as e:
                    st.error(f"Error creating timeline: {str(e)}")
                    st.info("Timeline feature temporarily unavailable. Other performance metrics above are still accurate.")
                
                # Data coverage information
                coverage = performance_results.get("data_coverage", {})
                if coverage:
                    with st.expander("ℹ️ Data Coverage Information"):
                        st.write(f"**Analysis Period:** {coverage.get('start_date', 'N/A')} to {coverage.get('end_date', 'N/A')}")
                        st.write(f"**Total Data Points:** {coverage.get('total_days', 'N/A')} days")
                        st.write(f"**Years Covered:** {coverage.get('years_covered', 'N/A')} years")
                        st.write("""
                        **Data Sources:**
                        - Time Deposits: Singapore Fixed Deposit rates
                        - Money Market Funds: SORA rates
                        - Multi-Asset Funds: MSCI World index
                        - Bond Funds: Singapore government bonds
                        - Cash: SORA rates
                        """)
            else:
                st.warning("Historical performance data not available. Please ensure market data is loaded.")
                
        except Exception as e:
            st.error(f"Error loading historical performance: {str(e)}")
            st.info("Historical performance analysis requires market data. Please check your data sources.")
    
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