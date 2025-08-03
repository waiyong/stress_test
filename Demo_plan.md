# 📊 Investment Committee Demo Plan
## Church Asset Risk & Stress Testing Dashboard

**Meeting Date**: August 4, 2025  
**Duration**: 20-25 minutes  
**Presenter**: Technical Team  
**Audience**: CPC Investment Committee  

---

## 🎯 Demo Objectives

### **Primary Goal**
Demonstrate how the dashboard empowers the Investment Committee with data-driven risk assessment for church portfolio management.

### **Key Messages**
1. **Professional Risk Management**: Move from intuition-based to data-driven investment decisions
2. **Business Assumption Validation**: Confirm OPEX (SGD 2.4M) and reserve requirements (12 months vs industry 3-6 months)
3. **Real Market Integration**: Live Singapore market data for accurate risk assessment
4. **Scenario Planning**: Test portfolio resilience against historical and hypothetical crises

### **Expected Outcomes**
- ✅ Validate annual OPEX assumptions (SGD 2.4M vs actual expenses)
- ✅ Decide on reserve coverage requirement (12 vs 3-6 months industry standard)
- ✅ Approve deployment with confirmed business parameters
- ✅ Establish regular stress testing process for IC meetings

---

## 📋 Demo Structure (20-25 minutes)

### **1. Opening Context (3 minutes)**

#### **Hook Statement**
*"Imagine it's March 2020, COVID just hit, markets are crashing 30%. The IC needs to know: Can we keep the church running? Do we have enough reserves? Should we sell investments or ride it out? This dashboard answers those questions with real data."*

#### **Current Challenge**
- How do we know if our SGD 3.4M portfolio can weather financial storms?
- Investment decisions currently based on intuition rather than data
- Need professional risk management tools for fiduciary responsibility

#### **Our Solution**
- Real-time dashboard with Singapore market data integration
- Professional-grade stress testing used by major investment committees
- Data-driven insights for informed decision making

---

### **2. Portfolio Overview Demo (4 minutes)**

#### **Current Portfolio Composition** (SGD 3.4M total)
- **Time Deposits**: SGD 1.3M (38%) - Conservative foundation
- **Money Market Funds**: SGD 1.0M (29%) - Liquid reserves  
- **Multi-Asset Funds**: SGD 550K (16%) - Growth component
- **Bond Funds**: SGD 350K (10%) - Stable income
- **Cash**: SGD 200K (7%) - Emergency buffer

#### **Key Demo Points**
1. **Live portfolio visualization** with real amounts
2. **Asset allocation pie chart** showing current diversification
3. **Liquidity profile** showing access timeframes:
   - **Immediate (0 days)**: SGD 200K (Cash)
   - **1-3 days**: SGD 1M (Money Market Funds)
   - **5-30 days**: SGD 900K (Bonds + Multi-Asset)
   - **180-365 days**: SGD 1.3M (Time Deposits - locked until maturity)

#### **Business Value**
*"This shows us exactly where our money is and how quickly we can access it during different scenarios."*

---

### **3. Real Market Data Integration (3 minutes)**

#### **Live Data Sources**
- **Singapore Rates**: SORA at 2.34%, Fixed Deposit rates at 3.10%
- **Market Indices** (with ticker symbols):
  - **STI**: ^STI (Singapore Straits Times Index)
  - **MSCI World**: URTH ETF (tracks MSCI World Index)
  - **MSCI Asia**: AAXJ ETF (tracks MSCI Asia ex-Japan)
- **Historical Coverage**: 7+ years of real Singapore market data including COVID period

#### **Technical Infrastructure**
- **Data Source**: OpenBB Platform (professional-grade financial data)
- **Updates**: Automatic daily updates via GitHub Actions (weekdays 6 PM Singapore)
- **Reliability**: Triple fallback system (Live data → Cache → Mock data)

#### **Business Value**
*"We're making decisions based on actual market conditions happening right now, not outdated assumptions."*

---

### **4. Risk Metrics Deep Dive (8 minutes)**

#### **Understanding the Risk Metrics Tab (4 minutes)**

Navigate to **Risk Metrics tab** and explain the three key gauges:

##### **A. Maximum Drawdown (%)**
- **What it means**: "How much would our portfolio value drop in this crisis?"
- **Calculation**: (Original Value - Stressed Value) / Original Value
- **Example**: If portfolio drops from SGD 3.4M to SGD 3.3M = 3% drawdown
- **Color coding**: 
  - ✅ **Green**: Less than 20% decline (safe)
  - 🔴 **Red**: More than 20% decline (significant risk)
- **Understanding the delta**: "3% with red arrow -17" means:
  - Portfolio declined 3%
  - This is 17 percentage points BETTER than the 20% danger threshold
  - Red arrow = favorable direction (lower decline is better)

##### **B. Reserve Coverage (%)**
- **What it means**: "After crisis, can we still cover church operations?"
- **Calculation**: Stressed Portfolio Value ÷ Annual OPEX (SGD 2.4M)
- **Target**: 100% = 12 months coverage minimum
- **Example**: 117% = 14.4 months of reserves after stress
- **Color coding**:
  - ✅ **Green**: Above 100% (adequate reserves)
  - 🔴 **Red**: Below 100% (insufficient reserves)

##### **C. Liquidity Time (Days)**
- **What it means**: "How long to access our money during crisis?"
- **Calculation**: Weighted average based on asset amounts and access times
- **Example calculation**:
  ```
  Cash (SGD 200K × 0 days) + MMF (SGD 1M × 1 day) + 
  Bonds (SGD 350K × 5 days) + Multi-Asset (SGD 550K × 30 days) + 
  Time Deposits (SGD 1.3M × 180 days) + Crisis delays
  = ~45-75 days average access time
  ```
- **Threshold**: 
  - ✅ **Green**: Less than 90 days (adequate liquidity)
  - 🔴 **Red**: More than 90 days (liquidity concern)

#### **Interactive Risk Testing (4 minutes)**

##### **Scenario A: Conservative Stress** (1 minute)
- **Select**: "Conservative" preset scenario
- **Parameters**: Interest rate cut -0.5%, market drop -15%, 5-day redemption freeze
- **Expected Results**:
  - Max Drawdown: ~3% (very mild impact)
  - Reserve Coverage: ~117% (strong position - 14.4 months reserves)
  - Liquidity Time: ~45 days (adequate access)
- **Message**: *"We easily weather mild economic slowdowns with strong reserves."*

##### **Scenario B: COVID-19 Stress** (1.5 minutes)
- **Select**: "COVID-19 Scenario" preset
- **Parameters**: Market drop -33%, interest rate cut -1.5%, 14-day redemption freeze
- **Expected Results**:
  - Max Drawdown: ~17% (significant but manageable)
  - Reserve Coverage: ~108% (still above 12-month requirement)
  - Liquidity Time: ~65 days (reasonable access time)
- **Message**: *"We would have survived COVID-19 with adequate reserves to spare."*

##### **Scenario C: 2008 Financial Crisis** (1.5 minutes)
- **Select**: "2008 Financial Crisis" preset
- **Parameters**: Market drop -37%, severe liquidity freeze 21 days
- **Expected Results**:
  - Max Drawdown: ~22% (crosses 20% danger threshold - red flag)
  - Reserve Coverage: ~102% (barely above 12-month requirement)
  - Liquidity Time: ~85 days (approaching 90-day concern level)
- **Message**: *"Even in the worst historical crisis, we maintain minimum reserves, but with little margin for error."*

---

### **5. Portfolio Composition Analysis (3 minutes)**

#### **Understanding "Portfolio Composition (Post-Stress)"**
- **What it shows**: Asset allocation AFTER stress factors are applied
- **Key insight**: Shows how portfolio balance shifts under pressure
- **Example**: 
  - **Before stress**: Time deposits 38%, Multi-Asset 16%
  - **After crisis**: Time deposits 42%, Multi-Asset 11% (conservative assets become larger percentage)

#### **Strategic Value**
1. **Risk Assessment**: See which assets provide stability vs growth
2. **Rebalancing Signals**: Identify if stressed portfolio becomes too concentrated
3. **Asset Allocation Planning**: Understand true diversification during crisis
4. **Liquidity Profile**: Shows actual accessible funds after crisis impact

#### **Business Message**
*"This tells us how our investment mix would actually look after a crisis hits, helping us plan our asset allocation strategy."*

---

### **6. Business Assumption Validation (4 minutes)**

#### **Critical Discussion Points**

##### **Annual OPEX Assumption** ⚠️ **REQUIRES IC VALIDATION**
- **Current Setting**: SGD 2.4M
- **Key Questions**:
  - "Is SGD 2.4M accurate for our church's actual annual operating expenses?"
  - "Should we use last year's actuals, this year's budget, or a 3-year average?"
  - "Do we include capital expenses or just operational costs?"
- **Impact Demonstration**: 
  - Change OPEX setting and show how all reserve coverage metrics update
  - Show difference between SGD 2.0M vs SGD 2.8M OPEX assumptions

##### **Reserve Requirement Policy** ⚠️ **REQUIRES IC DECISION**
- **Current Setting**: 12 months coverage required
- **Industry Context**: Standard church/nonprofit practice is 3-6 months
- **Key Questions**:
  - "Should we align with industry standard (3-6 months) or maintain conservative 12-month policy?"
  - "What's our risk tolerance for reserve adequacy?"
  - "How does this align with our board-approved financial policies?"
- **Impact Demonstration**:
  - Show scenarios with 6-month vs 12-month requirements
  - 6-month target: Most scenarios show "excess reserves"
  - 12-month target: Some scenarios show "borderline adequacy"

#### **Validation Process**
1. **Record IC decisions** on OPEX amount and reserve months
2. **Update system settings** with confirmed parameters
3. **Re-run stress tests** with validated assumptions
4. **Document decisions** for board reporting and audit trail

---

### **7. PDF Report Generation (2 minutes)**

#### **Professional Reporting Capability**
- **Generate**: Timestamped PDF report (e.g., "CPC_StressTest_2025-08-04_14-30.pdf")
- **Contents**:
  - Executive summary with key findings
  - Portfolio composition pre/post stress
  - Risk metrics summary with color-coded alerts
  - Scenario parameters and assumptions
  - Business insights and recommendations
- **Usage**: Download for IC meeting records, board reporting, audit documentation

#### **Business Value**
*"Professional documentation for investment decisions, board reports, and audit compliance."*

---

## 🎭 Demo Flow & Talking Points

### **Opening Transitions**
- **Portfolio Overview** → *"This is where we are today with our SGD 3.4M portfolio"*
- **Market Data** → *"This is what's happening in real Singapore markets right now"*  
- **Risk Metrics** → *"This is how we scientifically measure our financial safety"*
- **Scenarios** → *"This is how we prepare for and test different crisis situations"*
- **Reports** → *"This is how we document our analysis for board and audit requirements"*

### **Key Validation Moments**
- **OPEX Confirmation**: *"Let's pause here - is SGD 2.4M accurate for our actual annual expenses?"*
- **Reserve Policy**: *"Industry standard is 3-6 months reserves, we're using 12. Should we reconsider our conservative approach?"*
- **Risk Tolerance**: *"Based on these stress test results, are we comfortable with our current portfolio allocation?"*

### **Engagement Questions**
- *"What scenarios concern you most as IC members?"*
- *"How often should we run these stress tests - monthly, quarterly?"*
- *"What additional 'what-if' scenarios would be valuable for our planning?"*

---

## 📊 Risk Metrics Reference Card

### **Maximum Drawdown Interpretation**
- **Value Display**: Percentage portfolio decline under stress
- **Delta Indicator**: Difference from 20% danger threshold
- **Example**: "3% with -17 delta" means:
  - Portfolio declined by 3%
  - This is 17 percentage points BETTER than 20% threshold
  - Red arrow pointing down = favorable (lower decline is better)
- **Color Coding**: Green bar if <20%, Red bar if >20%

### **Reserve Coverage Interpretation**
- **Value Display**: Percentage of required reserve coverage
- **Delta Indicator**: Difference from 100% minimum requirement
- **Example**: "117% with +17 delta" means:
  - 117% of required reserves maintained
  - This is 17 percentage points ABOVE 100% minimum
  - Equals 14.4 months of coverage (12 × 1.17)
- **Color Coding**: Green bar if >100%, Red bar if <100%

### **Liquidity Time Interpretation**
- **Value Display**: Weighted average days to access portfolio funds
- **Delta Indicator**: Difference from 90-day threshold
- **Example**: "45 days with -45 delta" means:
  - 45 days average access time
  - This is 45 days BETTER than 90-day threshold
  - Green arrow = favorable (faster access is better)
- **Color Coding**: Green bar if <90 days, Red bar if >90 days

---

## 💼 Strategic Business Questions

### **Immediate Decisions Required**
1. **Annual OPEX Confirmation**: "What's our actual annual operating expense figure?"
2. **Reserve Policy**: "12-month vs 3-6 month industry standard - what's our preference?"
3. **Risk Tolerance**: "What level of portfolio volatility are we comfortable with?"
4. **Testing Frequency**: "How often should we conduct these stress tests?"

### **Strategic Planning Discussions**
1. **Portfolio Rebalancing**: "Should we adjust our asset allocation based on these results?"
2. **Liquidity Management**: "Is our current cash/MMF allocation adequate for crisis scenarios?"
3. **Investment Policy**: "How do we integrate stress testing into our investment committee process?"
4. **Board Reporting**: "How do we present these findings to the board?"

---

## 🎯 Next Steps Post-Demo

### **Immediate Actions (This Week)**
1. **Confirm Business Assumptions**: Update OPEX and reserve requirements based on IC input
2. **Deploy Production System**: Launch dashboard with validated parameters
3. **Schedule Regular Testing**: Establish monthly/quarterly stress testing schedule

### **Ongoing Implementation (Next Month)**
1. **IC Training**: Hands-on training for independent dashboard usage
2. **Policy Integration**: Incorporate stress testing into investment policy documentation
3. **Board Presentation**: Present system and initial findings to church board
4. **Audit Documentation**: Establish stress testing records for annual audit

### **Future Enhancements (As Needed)**
1. **Additional Scenarios**: Custom crisis scenarios based on IC input
2. **Portfolio Comparison**: Historical performance analysis capabilities
3. **Alert System**: Automated monitoring for significant market changes
4. **Advanced Analytics**: Monte Carlo simulations and correlation analysis

---

## 📞 Technical Support Information

### **Dashboard Access**
- **Local URL**: `http://localhost:8501` (during demo)
- **Production URL**: TBD (post-deployment)
- **System Requirements**: Web browser, internet connection for real-time data

### **Data Sources & Updates**
- **Market Data**: OpenBB Platform (professional financial data)
- **Update Schedule**: Weekdays 6 PM Singapore time (automated)
- **Backup Systems**: Local cache + mock data fallbacks
- **Historical Coverage**: 2018-present (7+ years including COVID period)

### **Support Contacts**
- **Technical Issues**: Development team
- **User Training**: Available upon request
- **Documentation**: Complete user guides in `/docs` folder

---

*This demo positions the dashboard as a professional investment management tool while securing critical business assumption validation needed for production deployment.*