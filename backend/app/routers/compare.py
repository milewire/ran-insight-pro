from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime

from ..db.session import get_db
from ..db.models import Upload, AnalysisResult
from ..services.parser import KPIParser
from ..services.anomaly import AnomalyDetector
from ..services.correlation import CorrelationEngine
from ..utils.logger import analysis_logger
from .auth import get_current_user

router = APIRouter(prefix="/compare", tags=["comparison"])

# Initialize services
parser = KPIParser()
anomaly_detector = AnomalyDetector()
correlation_engine = CorrelationEngine()

@router.post("/before-after")
async def compare_before_after_analysis(
    before_file: UploadFile = File(...),
    after_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Compare KPI data before and after an event (e.g., upgrade, optimization)
    
    Args:
        before_file: CSV file with KPI data before the event
        after_file: CSV file with KPI data after the event
        db: Database session
        
    Returns:
        Comparison analysis results
    """
    try:
        # Validate files
        if not (before_file.filename.endswith('.csv') and after_file.filename.endswith('.csv')):
            raise HTTPException(status_code=400, detail="Both files must be CSV format")
        
        # Parse both files
        before_content = await before_file.read()
        after_content = await after_file.read()
        
        before_df, before_metadata = parser.parse_csv(before_content, before_file.filename)
        after_df, after_metadata = parser.parse_csv(after_content, after_file.filename)
        
        # Perform individual analyses
        before_anomalies = anomaly_detector.detect_anomalies(before_df)
        after_anomalies = anomaly_detector.detect_anomalies(after_df)
        
        before_correlations = correlation_engine.analyze_correlations(before_df)
        after_correlations = correlation_engine.analyze_correlations(after_df)
        
        # Calculate comparison metrics
        comparison_results = _calculate_comparison_metrics(
            before_df, after_df, before_anomalies, after_anomalies,
            before_correlations, after_correlations
        )
        
        # Generate improvement assessment
        improvement_assessment = _assess_improvements(comparison_results)
        
        # Log comparison
        analysis_logger.log_analysis_complete(
            filename=f"{before_file.filename} vs {after_file.filename}",
            records_processed=len(before_df) + len(after_df),
            anomalies_found=comparison_results['total_anomalies_change'],
            user_id="anonymous"
        )
        
        return {
            "comparison_metadata": {
                "before_file": before_file.filename,
                "after_file": after_file.filename,
                "before_records": len(before_df),
                "after_records": len(after_df),
                "comparison_timestamp": datetime.utcnow().isoformat()
            },
            "kpi_comparison": comparison_results['kpi_comparison'],
            "anomaly_comparison": comparison_results['anomaly_comparison'],
            "correlation_comparison": comparison_results['correlation_comparison'],
            "improvement_assessment": improvement_assessment,
            "summary": comparison_results['summary']
        }
        
    except Exception as e:
        analysis_logger.log_analysis_error(
            filename=f"{before_file.filename} vs {after_file.filename}",
            error=str(e),
            user_id="anonymous"
        )
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@router.post("/baseline")
async def compare_with_baseline(
    current_file: UploadFile = File(...),
    baseline_upload_id: int = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Compare current KPI data with a baseline analysis
    
    Args:
        current_file: Current KPI data file
        baseline_upload_id: ID of baseline analysis in database
        db: Database session
        
    Returns:
        Comparison with baseline results
    """
    try:
        # Parse current file
        current_content = await current_file.read()
        current_df, current_metadata = parser.parse_csv(current_content, current_file.filename)
        
        # Get baseline analysis
        if baseline_upload_id:
            baseline_analysis = db.query(AnalysisResult).filter(
                AnalysisResult.upload_id == baseline_upload_id
            ).first()
            
            if not baseline_analysis:
                raise HTTPException(status_code=404, detail="Baseline analysis not found")
            
            # Create baseline metrics from stored analysis
            baseline_metrics = {
                'rtwp_mean': baseline_analysis.rtwp_mean,
                'rtwp_std': baseline_analysis.rtwp_std,
                'sinr_mean': baseline_analysis.sinr_mean,
                'sinr_std': baseline_analysis.sinr_std,
                'prb_mean': baseline_analysis.prb_mean,
                'prb_std': baseline_analysis.prb_std,
                'rtwp_anomalies': baseline_analysis.rtwp_anomalies,
                'sinr_anomalies': baseline_analysis.sinr_anomalies,
                'prb_anomalies': baseline_analysis.prb_anomalies
            }
        else:
            # Use default baseline values (industry standards)
            baseline_metrics = {
                'rtwp_mean': -95.0,  # Typical RTWP baseline
                'rtwp_std': 3.0,
                'sinr_mean': 15.0,   # Typical SINR baseline
                'sinr_std': 2.0,
                'prb_mean': 60.0,    # Typical PRB baseline
                'prb_std': 15.0,
                'rtwp_anomalies': 0,
                'sinr_anomalies': 0,
                'prb_anomalies': 0
            }
        
        # Analyze current data
        current_anomalies = anomaly_detector.detect_anomalies(current_df)
        current_correlations = correlation_engine.analyze_correlations(current_df)
        
        # Calculate current metrics
        current_metrics = {
            'rtwp_mean': float(current_df['RTWP'].mean()) if 'RTWP' in current_df.columns else None,
            'rtwp_std': float(current_df['RTWP'].std()) if 'RTWP' in current_df.columns else None,
            'sinr_mean': float(current_df['SINR'].mean()) if 'SINR' in current_df.columns else None,
            'sinr_std': float(current_df['SINR'].std()) if 'SINR' in current_df.columns else None,
            'prb_mean': float(current_df['PRB'].mean()) if 'PRB' in current_df.columns else None,
            'prb_std': float(current_df['PRB'].std()) if 'PRB' in current_df.columns else None,
            'rtwp_anomalies': current_anomalies['rtwp_anomalies']['count'],
            'sinr_anomalies': current_anomalies['sinr_anomalies']['count'],
            'prb_anomalies': current_anomalies['prb_anomalies']['count']
        }
        
        # Calculate deviations from baseline
        deviations = _calculate_baseline_deviations(baseline_metrics, current_metrics)
        
        # Assess performance against baseline
        performance_assessment = _assess_baseline_performance(deviations, current_anomalies)
        
        return {
            "comparison_metadata": {
                "current_file": current_file.filename,
                "baseline_upload_id": baseline_upload_id,
                "current_records": len(current_df),
                "comparison_timestamp": datetime.utcnow().isoformat()
            },
            "baseline_metrics": baseline_metrics,
            "current_metrics": current_metrics,
            "deviations": deviations,
            "performance_assessment": performance_assessment,
            "anomaly_analysis": current_anomalies,
            "correlation_analysis": current_correlations
        }
        
    except Exception as e:
        analysis_logger.log_analysis_error(
            filename=current_file.filename,
            error=str(e),
            user_id="anonymous"
        )
        raise HTTPException(status_code=500, detail=f"Baseline comparison failed: {str(e)}")

def _calculate_comparison_metrics(
    before_df: pd.DataFrame, after_df: pd.DataFrame,
    before_anomalies: Dict, after_anomalies: Dict,
    before_correlations: Dict, after_correlations: Dict
) -> Dict[str, Any]:
    """Calculate detailed comparison metrics between before and after data"""
    
    # KPI comparison
    kpi_comparison = {}
    for metric in ['RTWP', 'SINR', 'PRB']:
        if metric in before_df.columns and metric in after_df.columns:
            before_mean = before_df[metric].mean()
            after_mean = after_df[metric].mean()
            before_std = before_df[metric].std()
            after_std = after_df[metric].std()
            
            kpi_comparison[metric] = {
                'before_mean': float(before_mean),
                'after_mean': float(after_mean),
                'mean_change': float(after_mean - before_mean),
                'mean_change_percent': float((after_mean - before_mean) / before_mean * 100) if before_mean != 0 else 0,
                'before_std': float(before_std),
                'after_std': float(after_std),
                'std_change': float(after_std - before_std),
                'improvement': _assess_kpi_improvement(metric, before_mean, after_mean)
            }
    
    # Anomaly comparison
    anomaly_comparison = {
        'before_total': before_anomalies['summary']['total_anomalies'],
        'after_total': after_anomalies['summary']['total_anomalies'],
        'total_change': after_anomalies['summary']['total_anomalies'] - before_anomalies['summary']['total_anomalies'],
        'before_severity': before_anomalies['summary']['severity'],
        'after_severity': after_anomalies['summary']['severity'],
        'severity_improvement': _assess_severity_improvement(
            before_anomalies['summary']['severity'],
            after_anomalies['summary']['severity']
        )
    }
    
    # Correlation comparison
    correlation_comparison = {}
    before_pairwise = before_correlations['pairwise_correlations']
    after_pairwise = after_correlations['pairwise_correlations']
    
    for pair in ['RTWP_SINR', 'RTWP_PRB', 'SINR_PRB']:
        if pair in before_pairwise and pair in after_pairwise:
            before_corr = before_pairwise[pair]['correlation']
            after_corr = after_pairwise[pair]['correlation']
            
            correlation_comparison[pair] = {
                'before_correlation': before_corr,
                'after_correlation': after_corr,
                'correlation_change': after_corr - before_corr,
                'stability_change': _assess_correlation_stability_change(
                    before_corr, after_corr
                )
            }
    
    # Summary
    total_anomalies_change = anomaly_comparison['total_change']
    kpi_improvements = sum(1 for kpi in kpi_comparison.values() if kpi['improvement'] == 'improved')
    
    summary = {
        'overall_assessment': _generate_overall_assessment(total_anomalies_change, kpi_improvements),
        'key_improvements': _identify_key_improvements(kpi_comparison, anomaly_comparison),
        'areas_of_concern': _identify_areas_of_concern(kpi_comparison, anomaly_comparison)
    }
    
    return {
        'kpi_comparison': kpi_comparison,
        'anomaly_comparison': anomaly_comparison,
        'correlation_comparison': correlation_comparison,
        'total_anomalies_change': total_anomalies_change,
        'summary': summary
    }

def _assess_improvements(comparison_results: Dict) -> Dict[str, Any]:
    """Assess overall improvements from the comparison"""
    
    total_anomalies_change = comparison_results['total_anomalies_change']
    kpi_comparison = comparison_results['kpi_comparison']
    
    # Calculate improvement score
    improvement_score = 0
    max_score = 0
    
    # Anomaly improvement (40% weight)
    if total_anomalies_change < 0:
        improvement_score += 40  # Fewer anomalies is better
    max_score += 40
    
    # KPI improvements (60% weight)
    kpi_improvements = 0
    total_kpis = len(kpi_comparison)
    
    for metric, data in kpi_comparison.items():
        if data['improvement'] == 'improved':
            kpi_improvements += 1
        elif data['improvement'] == 'degraded':
            kpi_improvements -= 1
    
    if total_kpis > 0:
        kpi_score = (kpi_improvements / total_kpis) * 60
        improvement_score += kpi_score
    
    max_score += 60
    
    # Normalize score
    normalized_score = (improvement_score / max_score) * 100 if max_score > 0 else 0
    
    # Determine improvement level
    if normalized_score >= 80:
        improvement_level = 'significant'
    elif normalized_score >= 60:
        improvement_level = 'moderate'
    elif normalized_score >= 40:
        improvement_level = 'minimal'
    else:
        improvement_level = 'degraded'
    
    return {
        'improvement_score': normalized_score,
        'improvement_level': improvement_level,
        'anomaly_reduction': total_anomalies_change,
        'kpi_improvements': kpi_improvements,
        'total_kpis': total_kpis
    }

def _assess_kpi_improvement(metric: str, before_value: float, after_value: float) -> str:
    """Assess if a KPI has improved, degraded, or remained stable"""
    
    change_percent = abs((after_value - before_value) / before_value * 100) if before_value != 0 else 0
    
    if change_percent < 5:  # Less than 5% change is considered stable
        return 'stable'
    
    # Define improvement criteria for each metric
    if metric == 'RTWP':
        # Lower RTWP is better (less interference)
        return 'improved' if after_value < before_value else 'degraded'
    elif metric == 'SINR':
        # Higher SINR is better (better signal quality)
        return 'improved' if after_value > before_value else 'degraded'
    elif metric == 'PRB':
        # Moderate PRB utilization is better (not too high, not too low)
        if 40 <= after_value <= 80:
            return 'improved'
        elif 40 <= before_value <= 80:
            return 'degraded'
        else:
            return 'stable'
    else:
        return 'stable'

def _assess_severity_improvement(before_severity: str, after_severity: str) -> str:
    """Assess if anomaly severity has improved"""
    severity_levels = {'low': 1, 'medium': 2, 'high': 3}
    
    before_level = severity_levels.get(before_severity, 2)
    after_level = severity_levels.get(after_severity, 2)
    
    if after_level < before_level:
        return 'improved'
    elif after_level > before_level:
        return 'degraded'
    else:
        return 'stable'

def _assess_correlation_stability_change(before_corr: float, after_corr: float) -> str:
    """Assess if correlation stability has changed"""
    change = abs(after_corr - before_corr)
    
    if change < 0.1:
        return 'stable'
    elif change < 0.3:
        return 'moderate_change'
    else:
        return 'significant_change'

def _generate_overall_assessment(anomaly_change: int, kpi_improvements: int) -> str:
    """Generate overall assessment of the comparison"""
    if anomaly_change < -10 and kpi_improvements >= 2:
        return 'Significant improvement in network performance'
    elif anomaly_change < 0 and kpi_improvements >= 1:
        return 'Moderate improvement in network performance'
    elif anomaly_change == 0 and kpi_improvements == 0:
        return 'Network performance remained stable'
    elif anomaly_change > 0 and kpi_improvements == 0:
        return 'Network performance may have degraded'
    else:
        return 'Mixed results - some improvements and some degradations'

def _identify_key_improvements(kpi_comparison: Dict, anomaly_comparison: Dict) -> List[str]:
    """Identify key improvements from the comparison"""
    improvements = []
    
    if anomaly_comparison['total_change'] < 0:
        improvements.append(f"Reduced anomalies by {abs(anomaly_comparison['total_change'])}")
    
    for metric, data in kpi_comparison.items():
        if data['improvement'] == 'improved':
            improvements.append(f"{metric} improved by {data['mean_change_percent']:.1f}%")
    
    return improvements

def _identify_areas_of_concern(kpi_comparison: Dict, anomaly_comparison: Dict) -> List[str]:
    """Identify areas of concern from the comparison"""
    concerns = []
    
    if anomaly_comparison['total_change'] > 0:
        concerns.append(f"Increased anomalies by {anomaly_comparison['total_change']}")
    
    for metric, data in kpi_comparison.items():
        if data['improvement'] == 'degraded':
            concerns.append(f"{metric} degraded by {abs(data['mean_change_percent']):.1f}%")
    
    return concerns

def _calculate_baseline_deviations(baseline_metrics: Dict, current_metrics: Dict) -> Dict[str, Any]:
    """Calculate deviations from baseline metrics"""
    deviations = {}
    
    for metric in ['rtwp_mean', 'sinr_mean', 'prb_mean']:
        if metric in baseline_metrics and metric in current_metrics:
            baseline_val = baseline_metrics[metric]
            current_val = current_metrics[metric]
            
            if baseline_val is not None and current_val is not None:
                deviation = current_val - baseline_val
                deviation_percent = (deviation / baseline_val * 100) if baseline_val != 0 else 0
                
                deviations[metric] = {
                    'baseline_value': baseline_val,
                    'current_value': current_val,
                    'deviation': deviation,
                    'deviation_percent': deviation_percent,
                    'status': _assess_deviation_status(metric, deviation_percent)
                }
    
    return deviations

def _assess_deviation_status(metric: str, deviation_percent: float) -> str:
    """Assess if deviation from baseline is acceptable"""
    abs_deviation = abs(deviation_percent)
    
    if abs_deviation < 5:
        return 'within_normal_range'
    elif abs_deviation < 15:
        return 'minor_deviation'
    elif abs_deviation < 30:
        return 'significant_deviation'
    else:
        return 'major_deviation'

def _assess_baseline_performance(deviations: Dict, current_anomalies: Dict) -> Dict[str, Any]:
    """Assess overall performance against baseline"""
    
    total_deviations = len(deviations)
    acceptable_deviations = sum(1 for d in deviations.values() if d['status'] in ['within_normal_range', 'minor_deviation'])
    
    performance_score = (acceptable_deviations / total_deviations * 100) if total_deviations > 0 else 100
    
    anomaly_severity = current_anomalies['summary']['severity']
    
    if performance_score >= 80 and anomaly_severity == 'low':
        overall_status = 'excellent'
    elif performance_score >= 60 and anomaly_severity in ['low', 'medium']:
        overall_status = 'good'
    elif performance_score >= 40:
        overall_status = 'fair'
    else:
        overall_status = 'poor'
    
    return {
        'performance_score': performance_score,
        'overall_status': overall_status,
        'acceptable_deviations': acceptable_deviations,
        'total_deviations': total_deviations,
        'anomaly_severity': anomaly_severity
    }
