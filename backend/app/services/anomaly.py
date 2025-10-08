import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Detects anomalies in KPI data using statistical methods"""
    
    def __init__(self):
        self.anomaly_thresholds = {
            'rtwp_std_multiplier': 2.5,  # Standard deviations for RTWP
            'sinr_std_multiplier': 2.0,  # Standard deviations for SINR
            'prb_std_multiplier': 2.0,   # Standard deviations for PRB
            'rtwp_absolute_max': -70,    # RTWP should not exceed this (dBm)
            'rtwp_absolute_min': -120,   # RTWP should not go below this (dBm)
            'sinr_absolute_min': 0,      # SINR should not go below this (dB)
            'prb_absolute_max': 100,     # PRB should not exceed 100%
            'prb_absolute_min': 0,       # PRB should not go below 0%
        }
    
    def detect_anomalies(self, df: pd.DataFrame) -> Dict:
        """
        Detect anomalies in KPI data
        
        Args:
            df: DataFrame with RTWP, SINR, PRB columns
            
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            results = {
                'rtwp_anomalies': self._detect_rtwp_anomalies(df),
                'sinr_anomalies': self._detect_sinr_anomalies(df),
                'prb_anomalies': self._detect_prb_anomalies(df),
                'correlation_anomalies': self._detect_correlation_anomalies(df),
                'trend_anomalies': self._detect_trend_anomalies(df),
                'summary': {}
            }
            
            # Generate summary
            results['summary'] = self._generate_anomaly_summary(results)
            
            logger.info(f"Anomaly detection completed: {results['summary']['total_anomalies']} anomalies found")
            return results
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            raise
    
    def _detect_rtwp_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect RTWP anomalies"""
        if 'RTWP' not in df.columns:
            return {'count': 0, 'indices': [], 'types': []}
        
        anomalies = []
        anomaly_types = []
        
        # Statistical anomalies (outliers)
        mean_rtwp = df['RTWP'].mean()
        std_rtwp = df['RTWP'].std()
        threshold = self.anomaly_thresholds['rtwp_std_multiplier']
        
        statistical_outliers = abs(df['RTWP'] - mean_rtwp) > threshold * std_rtwp
        anomaly_indices = df[statistical_outliers].index.tolist()
        anomalies.extend(anomaly_indices)
        anomaly_types.extend(['statistical'] * len(anomaly_indices))
        
        # Absolute threshold anomalies
        high_rtwp = df['RTWP'] > self.anomaly_thresholds['rtwp_absolute_max']
        low_rtwp = df['RTWP'] < self.anomaly_thresholds['rtwp_absolute_min']
        
        high_indices = df[high_rtwp].index.tolist()
        low_indices = df[low_rtwp].index.tolist()
        
        anomalies.extend(high_indices)
        anomalies.extend(low_indices)
        anomaly_types.extend(['high_absolute'] * len(high_indices))
        anomaly_types.extend(['low_absolute'] * len(low_indices))
        
        # Remove duplicates while preserving order
        unique_anomalies = []
        unique_types = []
        seen = set()
        
        for i, idx in enumerate(anomalies):
            if idx not in seen:
                unique_anomalies.append(idx)
                unique_types.append(anomaly_types[i])
                seen.add(idx)
        
        return {
            'count': len(unique_anomalies),
            'indices': unique_anomalies,
            'types': unique_types,
            'mean': float(mean_rtwp),
            'std': float(std_rtwp)
        }
    
    def _detect_sinr_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect SINR anomalies"""
        if 'SINR' not in df.columns:
            return {'count': 0, 'indices': [], 'types': []}
        
        anomalies = []
        anomaly_types = []
        
        # Statistical anomalies
        mean_sinr = df['SINR'].mean()
        std_sinr = df['SINR'].std()
        threshold = self.anomaly_thresholds['sinr_std_multiplier']
        
        statistical_outliers = abs(df['SINR'] - mean_sinr) > threshold * std_sinr
        anomaly_indices = df[statistical_outliers].index.tolist()
        anomalies.extend(anomaly_indices)
        anomaly_types.extend(['statistical'] * len(anomaly_indices))
        
        # Absolute threshold anomalies
        low_sinr = df['SINR'] < self.anomaly_thresholds['sinr_absolute_min']
        low_indices = df[low_sinr].index.tolist()
        
        anomalies.extend(low_indices)
        anomaly_types.extend(['low_absolute'] * len(low_indices))
        
        # Remove duplicates
        unique_anomalies = []
        unique_types = []
        seen = set()
        
        for i, idx in enumerate(anomalies):
            if idx not in seen:
                unique_anomalies.append(idx)
                unique_types.append(anomaly_types[i])
                seen.add(idx)
        
        return {
            'count': len(unique_anomalies),
            'indices': unique_anomalies,
            'types': unique_types,
            'mean': float(mean_sinr),
            'std': float(std_sinr)
        }
    
    def _detect_prb_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect PRB utilization anomalies"""
        if 'PRB' not in df.columns:
            return {'count': 0, 'indices': [], 'types': []}
        
        anomalies = []
        anomaly_types = []
        
        # Statistical anomalies
        mean_prb = df['PRB'].mean()
        std_prb = df['PRB'].std()
        threshold = self.anomaly_thresholds['prb_std_multiplier']
        
        statistical_outliers = abs(df['PRB'] - mean_prb) > threshold * std_prb
        anomaly_indices = df[statistical_outliers].index.tolist()
        anomalies.extend(anomaly_indices)
        anomaly_types.extend(['statistical'] * len(anomaly_indices))
        
        # Absolute threshold anomalies
        high_prb = df['PRB'] > self.anomaly_thresholds['prb_absolute_max']
        low_prb = df['PRB'] < self.anomaly_thresholds['prb_absolute_min']
        
        high_indices = df[high_prb].index.tolist()
        low_indices = df[low_prb].index.tolist()
        
        anomalies.extend(high_indices)
        anomalies.extend(low_indices)
        anomaly_types.extend(['high_absolute'] * len(high_indices))
        anomaly_types.extend(['low_absolute'] * len(low_indices))
        
        # Remove duplicates
        unique_anomalies = []
        unique_types = []
        seen = set()
        
        for i, idx in enumerate(anomalies):
            if idx not in seen:
                unique_anomalies.append(idx)
                unique_types.append(anomaly_types[i])
                seen.add(idx)
        
        return {
            'count': len(unique_anomalies),
            'indices': unique_anomalies,
            'types': unique_types,
            'mean': float(mean_prb),
            'std': float(std_prb)
        }
    
    def _detect_correlation_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect anomalies in KPI correlations"""
        if not all(col in df.columns for col in ['RTWP', 'SINR', 'PRB']):
            return {'count': 0, 'description': 'Insufficient data for correlation analysis'}
        
        # Calculate rolling correlations
        window_size = min(20, len(df) // 4)  # Adaptive window size
        if window_size < 5:
            return {'count': 0, 'description': 'Insufficient data for correlation analysis'}
        
        rtwp_sinr_corr = df['RTWP'].rolling(window=window_size).corr(df['SINR'])
        rtwp_prb_corr = df['RTWP'].rolling(window=window_size).corr(df['PRB'])
        
        # Detect correlation breakdowns (correlation drops below -0.5 or above 0.5 unexpectedly)
        correlation_anomalies = []
        
        # RTWP-SINR correlation anomalies
        rtwp_sinr_anomalies = (rtwp_sinr_corr < -0.8) | (rtwp_sinr_corr > 0.8)
        correlation_anomalies.extend(df[rtwp_sinr_anomalies].index.tolist())
        
        # RTWP-PRB correlation anomalies
        rtwp_prb_anomalies = (rtwp_prb_corr < -0.8) | (rtwp_prb_corr > 0.8)
        correlation_anomalies.extend(df[rtwp_prb_anomalies].index.tolist())
        
        return {
            'count': len(set(correlation_anomalies)),
            'indices': list(set(correlation_anomalies)),
            'rtwp_sinr_correlation': float(df['RTWP'].corr(df['SINR'])),
            'rtwp_prb_correlation': float(df['RTWP'].corr(df['PRB'])),
            'sinr_prb_correlation': float(df['SINR'].corr(df['PRB']))
        }
    
    def _detect_trend_anomalies(self, df: pd.DataFrame) -> Dict:
        """Detect trend anomalies using moving averages"""
        if len(df) < 10:
            return {'count': 0, 'description': 'Insufficient data for trend analysis'}
        
        trend_anomalies = []
        
        for col in ['RTWP', 'SINR', 'PRB']:
            if col not in df.columns:
                continue
            
            # Calculate moving averages
            short_ma = df[col].rolling(window=5).mean()
            long_ma = df[col].rolling(window=15).mean()
            
            # Detect when short MA deviates significantly from long MA
            deviation = abs(short_ma - long_ma)
            threshold = df[col].std() * 2
            
            anomalies = df[deviation > threshold].index.tolist()
            trend_anomalies.extend(anomalies)
        
        return {
            'count': len(set(trend_anomalies)),
            'indices': list(set(trend_anomalies))
        }
    
    def _generate_anomaly_summary(self, results: Dict) -> Dict:
        """Generate summary of all anomaly detection results"""
        total_anomalies = (
            results['rtwp_anomalies']['count'] +
            results['sinr_anomalies']['count'] +
            results['prb_anomalies']['count'] +
            results['correlation_anomalies']['count'] +
            results['trend_anomalies']['count']
        )
        
        severity = 'low'
        if total_anomalies > 50:
            severity = 'high'
        elif total_anomalies > 20:
            severity = 'medium'
        
        return {
            'total_anomalies': total_anomalies,
            'severity': severity,
            'rtwp_anomaly_rate': results['rtwp_anomalies']['count'],
            'sinr_anomaly_rate': results['sinr_anomalies']['count'],
            'prb_anomaly_rate': results['prb_anomalies']['count'],
            'correlation_issues': results['correlation_anomalies']['count'],
            'trend_issues': results['trend_anomalies']['count']
        }
