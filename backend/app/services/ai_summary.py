import os
from typing import Dict, List, Optional
from openai import OpenAI
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AISummaryService:
    """Service for generating AI-powered analysis summaries using GPT"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    
    async def generate_analysis_summary(
        self, 
        kpi_stats: Dict, 
        anomaly_results: Dict, 
        correlation_results: Dict,
        metadata: Dict
    ) -> Dict:
        """
        Generate AI-powered analysis summary
        
        Args:
            kpi_stats: Statistical summaries of KPI data
            anomaly_results: Results from anomaly detection
            correlation_results: Results from correlation analysis
            metadata: File metadata and parsing information
            
        Returns:
            Dictionary with AI analysis results
        """
        try:
            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(
                kpi_stats, anomaly_results, correlation_results, metadata
            )
            
            # Generate AI response
            response = await self._call_openai_api(prompt)
            
            # Parse and structure the response
            analysis_result = self._parse_ai_response(response, kpi_stats, anomaly_results)
            
            logger.info("AI analysis summary generated successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            # Return fallback analysis
            return self._generate_fallback_analysis(kpi_stats, anomaly_results)
    
    def _build_analysis_prompt(
        self, 
        kpi_stats: Dict, 
        anomaly_results: Dict, 
        correlation_results: Dict,
        metadata: Dict
    ) -> str:
        """Build the analysis prompt for GPT"""
        
        prompt = f"""
You are a telecommunications network engineer analyzing RAN (Radio Access Network) KPI data. 
Analyze the following data and provide a comprehensive technical assessment:

## KPI Statistics:
- RTWP (Received Total Wideband Power): Mean={kpi_stats.get('rtwp_mean', 'N/A'):.1f} dBm, Std={kpi_stats.get('rtwp_std', 'N/A'):.1f}
- SINR (Signal-to-Interference-plus-Noise Ratio): Mean={kpi_stats.get('sinr_mean', 'N/A'):.1f} dB, Std={kpi_stats.get('sinr_std', 'N/A'):.1f}
- PRB (Physical Resource Block) Utilization: Mean={kpi_stats.get('prb_mean', 'N/A'):.1f}%, Std={kpi_stats.get('prb_std', 'N/A'):.1f}

## Anomaly Detection Results:
- Total Anomalies: {anomaly_results.get('summary', {}).get('total_anomalies', 0)}
- Severity Level: {anomaly_results.get('summary', {}).get('severity', 'unknown')}
- RTWP Anomalies: {anomaly_results.get('rtwp_anomalies', {}).get('count', 0)}
- SINR Anomalies: {anomaly_results.get('sinr_anomalies', {}).get('count', 0)}
- PRB Anomalies: {anomaly_results.get('prb_anomalies', {}).get('count', 0)}

## Correlation Analysis:
- RTWP-SINR Correlation: {correlation_results.get('pairwise_correlations', {}).get('RTWP_SINR', {}).get('correlation', 'N/A')}
- RTWP-PRB Correlation: {correlation_results.get('pairwise_correlations', {}).get('RTWP_PRB', {}).get('correlation', 'N/A')}
- SINR-PRB Correlation: {correlation_results.get('pairwise_correlations', {}).get('SINR_PRB', {}).get('correlation', 'N/A')}

## Data Quality:
- Total Records: {metadata.get('total_records', 'N/A')}
- Time Range: {metadata.get('time_range', {}).get('start', 'N/A')} to {metadata.get('time_range', {}).get('end', 'N/A')}

Please provide a technical analysis covering:

1. **Network Performance Assessment**: Evaluate the overall network health based on KPI values
2. **Anomaly Analysis**: Interpret the significance of detected anomalies and their potential causes
3. **Correlation Insights**: Explain what the correlations between metrics indicate about network behavior
4. **Root Cause Analysis**: Identify likely causes of any issues (e.g., interference, capacity, hardware problems)
5. **Recommendations**: Provide specific actionable recommendations for network optimization
6. **Risk Assessment**: Evaluate the severity and potential impact of identified issues

Focus on technical accuracy and provide specific, actionable insights that a network engineer can use for troubleshooting and optimization.
"""
        
        return prompt
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API to generate analysis"""
        if not self.client:
            raise Exception("OpenAI client not initialized. Please set OPENAI_API_KEY in environment variables.")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert telecommunications network engineer with deep knowledge of RAN optimization, interference analysis, and network troubleshooting. Provide technical, accurate, and actionable analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for more consistent technical analysis
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
    
    def _parse_ai_response(self, response: str, kpi_stats: Dict, anomaly_results: Dict) -> Dict:
        """Parse and structure the AI response"""
        
        # Calculate confidence score based on data quality and anomaly severity
        confidence_score = self._calculate_confidence_score(kpi_stats, anomaly_results)
        
        # Extract key sections from the response
        sections = self._extract_response_sections(response)
        
        return {
            'summary': response,
            'confidence_score': confidence_score,
            'sections': sections,
            'key_findings': self._extract_key_findings(response),
            'recommendations': self._extract_recommendations(response),
            'risk_level': self._assess_risk_level(anomaly_results, response)
        }
    
    def _calculate_confidence_score(self, kpi_stats: Dict, anomaly_results: Dict) -> float:
        """Calculate confidence score for the analysis"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on data quality
        total_records = kpi_stats.get('total_records', 0)
        if total_records > 1000:
            confidence += 0.1
        elif total_records < 100:
            confidence -= 0.2
        
        # Adjust based on anomaly severity
        anomaly_severity = anomaly_results.get('summary', {}).get('severity', 'low')
        if anomaly_severity == 'high':
            confidence -= 0.1  # High anomalies may indicate data quality issues
        elif anomaly_severity == 'low':
            confidence += 0.05
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _extract_response_sections(self, response: str) -> Dict:
        """Extract structured sections from the AI response"""
        sections = {
            'performance_assessment': '',
            'anomaly_analysis': '',
            'correlation_insights': '',
            'root_cause_analysis': '',
            'recommendations': '',
            'risk_assessment': ''
        }
        
        # Simple section extraction based on keywords
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in ['performance', 'network health', 'overall']):
                current_section = 'performance_assessment'
            elif any(keyword in line_lower for keyword in ['anomaly', 'outlier', 'unusual']):
                current_section = 'anomaly_analysis'
            elif any(keyword in line_lower for keyword in ['correlation', 'relationship', 'correlate']):
                current_section = 'correlation_insights'
            elif any(keyword in line_lower for keyword in ['root cause', 'cause', 'reason']):
                current_section = 'root_cause_analysis'
            elif any(keyword in line_lower for keyword in ['recommend', 'suggest', 'action']):
                current_section = 'recommendations'
            elif any(keyword in line_lower for keyword in ['risk', 'impact', 'severity']):
                current_section = 'risk_assessment'
            
            if current_section and line.strip():
                sections[current_section] += line + '\n'
        
        return sections
    
    def _extract_key_findings(self, response: str) -> List[str]:
        """Extract key findings from the AI response"""
        findings = []
        
        # Look for sentences that contain key technical terms
        sentences = response.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(term in sentence.lower() for term in [
                'interference', 'capacity', 'hardware', 'calibration', 
                'upgrade', 'optimization', 'critical', 'severe', 'warning'
            ]):
                if len(sentence) > 20:  # Avoid very short sentences
                    findings.append(sentence + '.')
        
        return findings[:5]  # Return top 5 findings
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from the AI response"""
        recommendations = []
        
        # Look for sentences that contain recommendation keywords
        sentences = response.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(term in sentence.lower() for term in [
                'recommend', 'suggest', 'should', 'consider', 'implement',
                'optimize', 'adjust', 'configure', 'upgrade'
            ]):
                if len(sentence) > 20:
                    recommendations.append(sentence + '.')
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _assess_risk_level(self, anomaly_results: Dict, response: str) -> str:
        """Assess the overall risk level based on anomalies and AI response"""
        anomaly_severity = anomaly_results.get('summary', {}).get('severity', 'low')
        
        # Check for critical keywords in AI response
        response_lower = response.lower()
        critical_keywords = ['critical', 'severe', 'urgent', 'immediate', 'failure']
        warning_keywords = ['warning', 'concern', 'issue', 'problem', 'degradation']
        
        if any(keyword in response_lower for keyword in critical_keywords):
            return 'critical'
        elif anomaly_severity == 'high' or any(keyword in response_lower for keyword in warning_keywords):
            return 'high'
        elif anomaly_severity == 'medium':
            return 'medium'
        else:
            return 'low'
    
    def _generate_fallback_analysis(self, kpi_stats: Dict, anomaly_results: Dict) -> Dict:
        """Generate fallback analysis when AI service is unavailable"""
        total_anomalies = anomaly_results.get('summary', {}).get('total_anomalies', 0)
        severity = anomaly_results.get('summary', {}).get('severity', 'low')
        
        if total_anomalies > 50:
            risk_level = 'high'
            summary = "High number of anomalies detected. Manual analysis recommended."
        elif total_anomalies > 20:
            risk_level = 'medium'
            summary = "Moderate anomalies detected. Network performance may be affected."
        else:
            risk_level = 'low'
            summary = "Low anomaly count. Network appears to be operating normally."
        
        return {
            'summary': summary,
            'confidence_score': 0.5,  # Lower confidence for fallback
            'sections': {'performance_assessment': summary},
            'key_findings': [f"Anomaly severity: {severity}", f"Total anomalies: {total_anomalies}"],
            'recommendations': ["Review anomaly details for specific issues", "Consider manual analysis if anomalies persist"],
            'risk_level': risk_level
        }
