"""
Basic tests for RAN Insight Pro backend
"""
import pytest
import pandas as pd
from datetime import datetime

from app.services.parser import KPIParser
from app.services.anomaly import AnomalyDetector
from app.services.correlation import CorrelationEngine

def test_kpi_parser():
    """Test KPI parser functionality"""
    parser = KPIParser()
    
    # Create sample CSV data
    sample_data = """TIME,RTWP,SINR,PRB
2024-01-01 00:00:00,-95.5,18.2,65.3
2024-01-01 00:15:00,-96.1,17.8,68.1
2024-01-01 00:30:00,-94.8,19.1,62.4
2024-01-01 00:45:00,-97.2,16.9,71.2"""
    
    # Test parsing
    df, metadata = parser.parse_csv(sample_data.encode('utf-8'), 'test.csv')
    
    assert len(df) == 4
    assert 'RTWP' in df.columns
    assert 'SINR' in df.columns
    assert 'PRB' in df.columns
    assert 'TIME' in df.columns
    assert metadata['total_records'] == 4

def test_anomaly_detector():
    """Test anomaly detection functionality"""
    detector = AnomalyDetector()
    
    # Create sample data with some anomalies
    data = {
        'RTWP': [-95, -96, -94, -70, -97, -98],  # -70 is an anomaly
        'SINR': [18, 19, 17, 20, 16, 18],
        'PRB': [65, 68, 62, 71, 69, 66]
    }
    df = pd.DataFrame(data)
    
    results = detector.detect_anomalies(df)
    
    assert 'rtwp_anomalies' in results
    assert 'summary' in results
    assert results['rtwp_anomalies']['count'] > 0  # Should detect the -70 anomaly

def test_correlation_engine():
    """Test correlation analysis functionality"""
    engine = CorrelationEngine()
    
    # Create sample data with known correlations
    data = {
        'RTWP': [-95, -96, -94, -97, -98, -99],
        'SINR': [18, 19, 17, 16, 15, 14],  # Negative correlation with RTWP
        'PRB': [65, 68, 62, 71, 69, 66]
    }
    df = pd.DataFrame(data)
    
    results = engine.analyze_correlations(df)
    
    assert 'pairwise_correlations' in results
    assert 'insights' in results
    assert 'RTWP_SINR' in results['pairwise_correlations']

def test_integration():
    """Test integration of all services"""
    parser = KPIParser()
    detector = AnomalyDetector()
    engine = CorrelationEngine()
    
    # Sample data
    sample_data = """TIME,RTWP,SINR,PRB
2024-01-01 00:00:00,-95.5,18.2,65.3
2024-01-01 00:15:00,-96.1,17.8,68.1
2024-01-01 00:30:00,-94.8,19.1,62.4
2024-01-01 00:45:00,-97.2,16.9,71.2
2024-01-01 01:00:00,-70.0,25.0,90.0"""  # Anomaly
    
    # Parse data
    df, metadata = parser.parse_csv(sample_data.encode('utf-8'), 'test.csv')
    
    # Detect anomalies
    anomalies = detector.detect_anomalies(df)
    
    # Analyze correlations
    correlations = engine.analyze_correlations(df)
    
    # Verify results
    assert len(df) == 5
    assert anomalies['summary']['total_anomalies'] > 0
    assert 'RTWP_SINR' in correlations['pairwise_correlations']

if __name__ == "__main__":
    # Run basic tests
    test_kpi_parser()
    test_anomaly_detector()
    test_correlation_engine()
    test_integration()
    print("All basic tests passed!")
