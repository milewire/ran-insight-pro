from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates PDF reports for KPI analysis results"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkgreen
        ))
    
    async def generate_analysis_report(
        self,
        kpi_data: pd.DataFrame,
        kpi_stats: Dict,
        anomaly_results: Dict,
        correlation_results: Dict,
        ai_analysis: Dict,
        metadata: Dict,
        filename: str = None
    ) -> bytes:
        """
        Generate a comprehensive PDF analysis report
        
        Args:
            kpi_data: Processed KPI DataFrame
            kpi_stats: Statistical summaries
            anomaly_results: Anomaly detection results
            correlation_results: Correlation analysis results
            ai_analysis: AI analysis results
            metadata: File metadata
            filename: Optional filename for the report
            
        Returns:
            PDF content as bytes
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build the report content
            story = []
            
            # Title page
            story.extend(self._build_title_page(metadata, ai_analysis))
            
            # Executive summary
            story.extend(self._build_executive_summary(ai_analysis, anomaly_results))
            
            # KPI statistics
            story.extend(self._build_kpi_statistics(kpi_stats))
            
            # Anomaly analysis
            story.extend(self._build_anomaly_analysis(anomaly_results))
            
            # Correlation analysis
            story.extend(self._build_correlation_analysis(correlation_results))
            
            # AI analysis
            story.extend(self._build_ai_analysis(ai_analysis))
            
            # Charts and visualizations
            story.extend(self._build_charts_section(kpi_data, kpi_stats))
            
            # Recommendations
            story.extend(self._build_recommendations(ai_analysis))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            logger.info("PDF report generated successfully")
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise
    
    def _build_title_page(self, metadata: Dict, ai_analysis: Dict) -> List:
        """Build the title page of the report"""
        elements = []
        
        # Title
        elements.append(Paragraph("RAN Insight Pro", self.styles['CustomTitle']))
        elements.append(Paragraph("Network Performance Analysis Report", self.styles['SectionHeader']))
        elements.append(Spacer(1, 20))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(f"<b>Report Date:</b> {report_date}", self.styles['Normal']))
        elements.append(Paragraph(f"<b>Data File:</b> {metadata.get('filename', 'N/A')}", self.styles['Normal']))
        elements.append(Paragraph(f"<b>Total Records:</b> {metadata.get('total_records', 'N/A')}", self.styles['Normal']))
        
        if metadata.get('time_range'):
            time_range = metadata['time_range']
            elements.append(Paragraph(
                f"<b>Analysis Period:</b> {time_range.get('start', 'N/A')} to {time_range.get('end', 'N/A')}",
                self.styles['Normal']
            ))
        
        elements.append(Spacer(1, 20))
        
        # Risk assessment
        risk_level = ai_analysis.get('risk_level', 'unknown')
        risk_color = self._get_risk_color(risk_level)
        elements.append(Paragraph(
            f"<b>Overall Risk Level:</b> <font color='{risk_color}'>{risk_level.upper()}</font>",
            self.styles['Normal']
        ))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_executive_summary(self, ai_analysis: Dict, anomaly_results: Dict) -> List:
        """Build the executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))
        
        # Key metrics
        total_anomalies = anomaly_results.get('summary', {}).get('total_anomalies', 0)
        severity = anomaly_results.get('summary', {}).get('severity', 'low')
        confidence = ai_analysis.get('confidence_score', 0)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Anomalies Detected', str(total_anomalies)],
            ['Anomaly Severity', severity.upper()],
            ['Analysis Confidence', f"{confidence:.1%}"],
            ['Risk Level', ai_analysis.get('risk_level', 'unknown').upper()]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 12))
        
        # AI summary
        ai_summary = ai_analysis.get('summary', 'No AI analysis available.')
        elements.append(Paragraph("<b>AI Analysis Summary:</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(ai_summary, self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_kpi_statistics(self, kpi_stats: Dict) -> List:
        """Build the KPI statistics section"""
        elements = []
        
        elements.append(Paragraph("KPI Statistics", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))
        
        # Create statistics table
        stats_data = [
            ['Metric', 'Mean', 'Standard Deviation', 'Min', 'Max'],
            [
                'RTWP (dBm)',
                f"{kpi_stats.get('rtwp_mean', 0):.1f}",
                f"{kpi_stats.get('rtwp_std', 0):.1f}",
                f"{kpi_stats.get('rtwp_min', 0):.1f}",
                f"{kpi_stats.get('rtwp_max', 0):.1f}"
            ],
            [
                'SINR (dB)',
                f"{kpi_stats.get('sinr_mean', 0):.1f}",
                f"{kpi_stats.get('sinr_std', 0):.1f}",
                f"{kpi_stats.get('sinr_min', 0):.1f}",
                f"{kpi_stats.get('sinr_max', 0):.1f}"
            ],
            [
                'PRB Utilization (%)',
                f"{kpi_stats.get('prb_mean', 0):.1f}",
                f"{kpi_stats.get('prb_std', 0):.1f}",
                f"{kpi_stats.get('prb_min', 0):.1f}",
                f"{kpi_stats.get('prb_max', 0):.1f}"
            ]
        ]
        
        stats_table = Table(stats_data, colWidths=[1.5*inch, 1*inch, 1.2*inch, 1*inch, 1*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_anomaly_analysis(self, anomaly_results: Dict) -> List:
        """Build the anomaly analysis section"""
        elements = []
        
        elements.append(Paragraph("Anomaly Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))
        
        # Anomaly summary
        summary = anomaly_results.get('summary', {})
        elements.append(Paragraph(f"<b>Total Anomalies:</b> {summary.get('total_anomalies', 0)}", self.styles['Normal']))
        elements.append(Paragraph(f"<b>Severity Level:</b> {summary.get('severity', 'unknown').upper()}", self.styles['Normal']))
        elements.append(Spacer(1, 8))
        
        # Detailed anomaly breakdown
        anomaly_data = [
            ['Metric', 'Anomaly Count', 'Anomaly Rate'],
            [
                'RTWP',
                str(anomaly_results.get('rtwp_anomalies', {}).get('count', 0)),
                f"{summary.get('rtwp_anomaly_rate', 0)}"
            ],
            [
                'SINR',
                str(anomaly_results.get('sinr_anomalies', {}).get('count', 0)),
                f"{summary.get('sinr_anomaly_rate', 0)}"
            ],
            [
                'PRB',
                str(anomaly_results.get('prb_anomalies', {}).get('count', 0)),
                f"{summary.get('prb_anomaly_rate', 0)}"
            ]
        ]
        
        anomaly_table = Table(anomaly_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        anomaly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(anomaly_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_correlation_analysis(self, correlation_results: Dict) -> List:
        """Build the correlation analysis section"""
        elements = []
        
        elements.append(Paragraph("Correlation Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))
        
        # Correlation matrix
        pairwise = correlation_results.get('pairwise_correlations', {})
        
        correlation_data = [
            ['Metric Pair', 'Correlation', 'Strength', 'Significance'],
            [
                'RTWP - SINR',
                f"{pairwise.get('RTWP_SINR', {}).get('correlation', 0):.3f}",
                pairwise.get('RTWP_SINR', {}).get('strength', 'unknown'),
                pairwise.get('RTWP_SINR', {}).get('significance', 'unknown')
            ],
            [
                'RTWP - PRB',
                f"{pairwise.get('RTWP_PRB', {}).get('correlation', 0):.3f}",
                pairwise.get('RTWP_PRB', {}).get('strength', 'unknown'),
                pairwise.get('RTWP_PRB', {}).get('significance', 'unknown')
            ],
            [
                'SINR - PRB',
                f"{pairwise.get('SINR_PRB', {}).get('correlation', 0):.3f}",
                pairwise.get('SINR_PRB', {}).get('strength', 'unknown'),
                pairwise.get('SINR_PRB', {}).get('significance', 'unknown')
            ]
        ]
        
        correlation_table = Table(correlation_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
        correlation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(correlation_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_ai_analysis(self, ai_analysis: Dict) -> List:
        """Build the AI analysis section"""
        elements = []
        
        elements.append(Paragraph("AI Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))
        
        # Key findings
        key_findings = ai_analysis.get('key_findings', [])
        if key_findings:
            elements.append(Paragraph("<b>Key Findings:</b>", self.styles['SubsectionHeader']))
            for finding in key_findings:
                elements.append(Paragraph(f"• {finding}", self.styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # Recommendations
        recommendations = ai_analysis.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("<b>Recommendations:</b>", self.styles['SubsectionHeader']))
            for rec in recommendations:
                elements.append(Paragraph(f"• {rec}", self.styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # Full AI summary
        full_summary = ai_analysis.get('summary', '')
        if full_summary:
            elements.append(Paragraph("<b>Detailed Analysis:</b>", self.styles['SubsectionHeader']))
            elements.append(Paragraph(full_summary, self.styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_charts_section(self, kpi_data: pd.DataFrame, kpi_stats: Dict) -> List:
        """Build the charts and visualizations section"""
        elements = []
        
        elements.append(Paragraph("Charts and Visualizations", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))
        
        # Note: In a real implementation, you would generate actual charts here
        # For now, we'll add a placeholder
        elements.append(Paragraph(
            "<i>Charts and visualizations would be generated here showing KPI trends, "
            "anomaly distributions, and correlation plots.</i>",
            self.styles['Normal']
        ))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_recommendations(self, ai_analysis: Dict) -> List:
        """Build the recommendations section"""
        elements = []
        
        elements.append(Paragraph("Recommendations and Next Steps", self.styles['SectionHeader']))
        elements.append(Spacer(1, 12))
        
        recommendations = ai_analysis.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                elements.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
        else:
            elements.append(Paragraph("No specific recommendations available.", self.styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level display"""
        risk_colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        return risk_colors.get(risk_level.lower(), 'black')
