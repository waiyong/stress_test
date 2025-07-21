"""
PDF report generation for Church Asset Risk & Stress Testing Dashboard
"""

import io
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from .config import REPORT_TITLE, REPORT_FILENAME_PREFIX


class ReportGenerator:
    def __init__(self):
        """Initialize PDF report generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.darkblue,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkred,
            alignment=TA_LEFT
        ))
        
        # Risk flag style
        self.styles.add(ParagraphStyle(
            name='RiskFlag',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.red,
            leftIndent=20
        ))
        
        # Success flag style
        self.styles.add(ParagraphStyle(
            name='SuccessFlag',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.green,
            leftIndent=20
        ))
        
    def generate_stress_test_report(self, metrics: Dict[str, Any], insights: List[str]) -> io.BytesIO:
        """Generate comprehensive stress test PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build report content
        story = []
        
        # Title and header
        story.extend(self._build_header(metrics))
        
        # Executive summary
        story.extend(self._build_executive_summary(metrics))
        
        # Key insights
        story.extend(self._build_insights_section(insights))
        
        # Detailed metrics
        story.extend(self._build_detailed_metrics(metrics))
        
        # Portfolio breakdown
        story.extend(self._build_portfolio_breakdown(metrics))
        
        # Stress parameters
        story.extend(self._build_stress_parameters(metrics))
        
        # Risk flags and recommendations
        story.extend(self._build_risk_assessment(metrics))
        
        # Footer
        story.extend(self._build_footer())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    def _build_header(self, metrics: Dict[str, Any]) -> List:
        """Build report header section"""
        story = []
        
        # Main title
        story.append(Paragraph(REPORT_TITLE, self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Report metadata
        timestamp = datetime.now().strftime("%d %B %Y at %H:%M SGT")
        story.append(Paragraph(f"<b>Report Generated:</b> {timestamp}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Scenario:</b> Custom Stress Test Parameters", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        return story
        
    def _build_executive_summary(self, metrics: Dict[str, Any]) -> List:
        """Build executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
        
        # Key numbers table
        summary_data = [
            ['Metric', 'Value', 'Status'],
            ['Original Portfolio Value', f"SGD {metrics['original_portfolio_value']:,.0f}", ''],
            ['Stressed Portfolio Value', f"SGD {metrics['stressed_portfolio_value']:,.0f}", ''],
            ['Portfolio Decline', f"{metrics['portfolio_decline_pct']*100:.1f}%", 
             '🔴 HIGH RISK' if metrics['volatility_breach_flag'] else '✅ ACCEPTABLE'],
            ['Reserve Coverage', f"{metrics['reserve_coverage_ratio']:.2f}x", 
             '🔴 INSUFFICIENT' if metrics['reserve_coverage_ratio'] < 1.0 else '✅ ADEQUATE'],
            ['Months of Reserves', f"{metrics['reserve_months_covered']:.1f} months", ''],
            ['Time to Liquidity', f"{metrics['time_to_liquidity_days']:.0f} days", 
             '🔴 SLOW ACCESS' if metrics['liquidity_breach_flag'] else '✅ REASONABLE']
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        return story
        
    def _build_insights_section(self, insights: List[str]) -> List:
        """Build key insights section"""
        story = []
        
        story.append(Paragraph("Key Insights & Recommendations", self.styles['CustomSubtitle']))
        
        for insight in insights:
            if '🔴' in insight or '⚠️' in insight:
                story.append(Paragraph(insight, self.styles['RiskFlag']))
            else:
                story.append(Paragraph(insight, self.styles['SuccessFlag']))
                
        story.append(Spacer(1, 20))
        
        return story
        
    def _build_detailed_metrics(self, metrics: Dict[str, Any]) -> List:
        """Build detailed metrics section"""
        story = []
        
        story.append(Paragraph("Detailed Risk Metrics", self.styles['CustomSubtitle']))
        
        # Create detailed metrics table
        metrics_data = [
            ['Risk Metric', 'Current Value', 'Threshold', 'Assessment'],
            ['Maximum Drawdown', f"{metrics['max_drawdown_pct']*100:.2f}%", "20.0%", 
             'BREACH' if metrics['volatility_breach_flag'] else 'WITHIN LIMITS'],
            ['Reserve Coverage Ratio', f"{metrics['reserve_coverage_ratio']:.3f}", "1.000", 
             'INSUFFICIENT' if metrics['reserve_coverage_ratio'] < 1.0 else 'ADEQUATE'],
            ['Liquidity Access Time', f"{metrics['time_to_liquidity_days']:.1f} days", "90 days", 
             'CONCERNING' if metrics['liquidity_breach_flag'] else 'ACCEPTABLE'],
            ['Annual OPEX Coverage', f"SGD {metrics['annual_opex_requirement']:,.0f}", "Required", 
             f"Covered for {metrics['reserve_months_covered']:.1f} months"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.2*inch, 1*inch, 1.3*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        return story
        
    def _build_portfolio_breakdown(self, metrics: Dict[str, Any]) -> List:
        """Build portfolio asset breakdown section"""
        story = []
        
        story.append(Paragraph("Portfolio Composition (Post-Stress)", self.styles['CustomSubtitle']))
        
        # Asset breakdown table
        breakdown_data = [['Asset Type', 'Amount (SGD)', 'Percentage', 'Count']]
        
        for asset_type, breakdown in metrics['asset_breakdown'].items():
            breakdown_data.append([
                asset_type.replace('_', ' '),
                f"{breakdown['amount_sgd']:,.0f}",
                f"{breakdown['percentage']:.1f}%",
                str(breakdown['count'])
            ])
            
        # Add total row
        breakdown_data.append([
            'TOTAL',
            f"{metrics['stressed_portfolio_value']:,.0f}",
            "100.0%",
            str(sum(b['count'] for b in metrics['asset_breakdown'].values()))
        ])
        
        breakdown_table = Table(breakdown_data, colWidths=[2*inch, 1.5*inch, 1*inch, 0.8*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        story.append(breakdown_table)
        story.append(Spacer(1, 20))
        
        return story
        
    def _build_stress_parameters(self, metrics: Dict[str, Any]) -> List:
        """Build stress test parameters section"""
        story = []
        
        story.append(Paragraph("Stress Test Parameters Applied", self.styles['CustomSubtitle']))
        
        # Parameters table
        params = metrics['stress_parameters']
        param_data = [['Parameter', 'Applied Value', 'Impact']]
        
        param_descriptions = {
            'interest_rate_shock': ('Interest Rate Shock', '%', 'Affects FD, MMF, and bond returns'),
            'inflation_spike': ('Inflation Spike', '%', 'Reduces real returns'),
            'multi_asset_drawdown': ('Multi-Asset Fund Decline', '%', 'Market crash simulation'),
            'redemption_freeze_days': ('Redemption Freeze Extension', ' days', 'Delays fund access'),
            'early_withdrawal_penalty': ('Early Withdrawal Penalty', '%', 'FD premature withdrawal cost'),
            'counterparty_risk': ('Counterparty Risk', '% loss', 'Institution failure simulation')
        }
        
        for param_key, value in params.items():
            if param_key in param_descriptions:
                desc, unit, impact = param_descriptions[param_key]
                if unit == '%':
                    formatted_value = f"{value*100:+.1f}%"
                elif unit == ' days':
                    formatted_value = f"{value:+.0f} days"
                else:
                    formatted_value = f"{value*100:+.1f}{unit}"
                    
                param_data.append([desc, formatted_value, impact])
        
        param_table = Table(param_data, colWidths=[2.2*inch, 1.3*inch, 2*inch])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(param_table)
        story.append(Spacer(1, 20))
        
        return story
        
    def _build_risk_assessment(self, metrics: Dict[str, Any]) -> List:
        """Build risk assessment and recommendations section"""
        story = []
        
        story.append(Paragraph("Risk Assessment Summary", self.styles['CustomSubtitle']))
        
        # Risk status
        if metrics['volatility_breach_flag'] or metrics['liquidity_breach_flag']:
            risk_level = "HIGH RISK"
            risk_color = "red"
        elif metrics['reserve_coverage_ratio'] < 1.2:
            risk_level = "MODERATE RISK"
            risk_color = "orange"
        else:
            risk_level = "LOW RISK"
            risk_color = "green"
            
        story.append(Paragraph(f"<b>Overall Risk Level: <font color='{risk_color}'>{risk_level}</font></b>", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Recommendations
        story.append(Paragraph("<b>Recommendations:</b>", self.styles['Normal']))
        
        recommendations = []
        
        if metrics['reserve_coverage_ratio'] < 1.0:
            recommendations.append("• Consider increasing cash reserves or reducing OPEX commitments")
            
        if metrics['volatility_breach_flag']:
            recommendations.append("• Review asset allocation to reduce portfolio volatility")
            recommendations.append("• Consider increasing allocation to stable assets (FDs, MMFs)")
            
        if metrics['liquidity_breach_flag']:
            recommendations.append("• Improve liquidity profile by reducing long-term FD allocations")
            recommendations.append("• Increase proportion of MMFs and cash equivalents")
            
        if not recommendations:
            recommendations.append("• Portfolio demonstrates good resilience under stress conditions")
            recommendations.append("• Consider regular stress testing to monitor ongoing risk levels")
            
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['Normal']))
            
        story.append(Spacer(1, 20))
        
        return story
        
    def _build_footer(self) -> List:
        """Build report footer"""
        story = []
        
        story.append(Spacer(1, 30))
        story.append(Paragraph("<i>This report is generated for internal investment committee review and planning purposes. "
                              "It is based on hypothetical stress scenarios and should not be considered as investment advice. "
                              "Consult with qualified financial advisors for investment decisions.</i>", 
                              self.styles['Normal']))
        
        return story
        
    def generate_filename(self, custom_suffix: str = None) -> str:
        """Generate standardized filename for reports"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        suffix = f"_{custom_suffix}" if custom_suffix else ""
        return f"{REPORT_FILENAME_PREFIX}_{timestamp}{suffix}.pdf"


# Convenience function
def generate_pdf_report(metrics: Dict[str, Any], insights: List[str]) -> io.BytesIO:
    """Convenience function to generate PDF report"""
    generator = ReportGenerator()
    return generator.generate_stress_test_report(metrics, insights)