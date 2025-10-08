import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

# Optional scipy import for advanced statistics
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)

class CorrelationEngine:
    """Analyzes correlations between KPI metrics"""
    
    def __init__(self):
        self.correlation_thresholds = {
            'strong_positive': 0.7,
            'moderate_positive': 0.3,
            'moderate_negative': -0.3,
            'strong_negative': -0.7
        }
    
    def analyze_correlations(self, df: pd.DataFrame) -> Dict:
        """
        Analyze correlations between KPI metrics
        
        Args:
            df: DataFrame with RTWP, SINR, PRB columns
            
        Returns:
            Dictionary with correlation analysis results
        """
        try:
            results = {
                'pairwise_correlations': self._calculate_pairwise_correlations(df),
                'rolling_correlations': self._calculate_rolling_correlations(df),
                'correlation_stability': self._analyze_correlation_stability(df),
                'cross_correlations': self._calculate_cross_correlations(df),
                'insights': []
            }
            
            # Generate insights
            results['insights'] = self._generate_correlation_insights(results)
            
            logger.info("Correlation analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in correlation analysis: {str(e)}")
            raise
    
    def _calculate_pairwise_correlations(self, df: pd.DataFrame) -> Dict:
        """Calculate pairwise correlations between KPI metrics"""
        correlations = {}
        
        kpi_columns = ['RTWP', 'SINR', 'PRB']
        available_columns = [col for col in kpi_columns if col in df.columns]
        
        for i, col1 in enumerate(available_columns):
            for j, col2 in enumerate(available_columns):
                if i < j:  # Avoid duplicate pairs
                    corr_coef = df[col1].corr(df[col2])
                    if SCIPY_AVAILABLE:
                        p_value = stats.pearsonr(df[col1].dropna(), df[col2].dropna())[1]
                    else:
                        # Simple p-value approximation without scipy
                        n = len(df[col1].dropna())
                        p_value = 0.05 if abs(corr_coef) > 0.3 else 0.1
                    
                    correlations[f"{col1}_{col2}"] = {
                        'correlation': float(corr_coef) if not np.isnan(corr_coef) else 0.0,
                        'p_value': float(p_value) if not np.isnan(p_value) else 1.0,
                        'strength': self._classify_correlation_strength(corr_coef),
                        'significance': 'significant' if p_value < 0.05 else 'not_significant'
                    }
        
        return correlations
    
    def _calculate_rolling_correlations(self, df: pd.DataFrame) -> Dict:
        """Calculate rolling correlations to detect time-varying relationships"""
        window_size = min(20, len(df) // 4)
        if window_size < 5:
            return {'error': 'Insufficient data for rolling correlation analysis'}
        
        rolling_correlations = {}
        
        # RTWP vs SINR rolling correlation
        if 'RTWP' in df.columns and 'SINR' in df.columns:
            rtwp_sinr_rolling = df['RTWP'].rolling(window=window_size).corr(df['SINR'])
            rolling_correlations['rtwp_sinr'] = {
                'mean': float(rtwp_sinr_rolling.mean()) if not rtwp_sinr_rolling.empty else 0.0,
                'std': float(rtwp_sinr_rolling.std()) if not rtwp_sinr_rolling.empty else 0.0,
                'min': float(rtwp_sinr_rolling.min()) if not rtwp_sinr_rolling.empty else 0.0,
                'max': float(rtwp_sinr_rolling.max()) if not rtwp_sinr_rolling.empty else 0.0,
                'stability': self._calculate_correlation_stability(rtwp_sinr_rolling)
            }
        
        # RTWP vs PRB rolling correlation
        if 'RTWP' in df.columns and 'PRB' in df.columns:
            rtwp_prb_rolling = df['RTWP'].rolling(window=window_size).corr(df['PRB'])
            rolling_correlations['rtwp_prb'] = {
                'mean': float(rtwp_prb_rolling.mean()) if not rtwp_prb_rolling.empty else 0.0,
                'std': float(rtwp_prb_rolling.std()) if not rtwp_prb_rolling.empty else 0.0,
                'min': float(rtwp_prb_rolling.min()) if not rtwp_prb_rolling.empty else 0.0,
                'max': float(rtwp_prb_rolling.max()) if not rtwp_prb_rolling.empty else 0.0,
                'stability': self._calculate_correlation_stability(rtwp_prb_rolling)
            }
        
        # SINR vs PRB rolling correlation
        if 'SINR' in df.columns and 'PRB' in df.columns:
            sinr_prb_rolling = df['SINR'].rolling(window=window_size).corr(df['PRB'])
            rolling_correlations['sinr_prb'] = {
                'mean': float(sinr_prb_rolling.mean()) if not sinr_prb_rolling.empty else 0.0,
                'std': float(sinr_prb_rolling.std()) if not sinr_prb_rolling.empty else 0.0,
                'min': float(sinr_prb_rolling.min()) if not sinr_prb_rolling.empty else 0.0,
                'max': float(sinr_prb_rolling.max()) if not sinr_prb_rolling.empty else 0.0,
                'stability': self._calculate_correlation_stability(sinr_prb_rolling)
            }
        
        return rolling_correlations
    
    def _analyze_correlation_stability(self, df: pd.DataFrame) -> Dict:
        """Analyze how stable correlations are over time"""
        window_size = min(20, len(df) // 4)
        if window_size < 5:
            return {'error': 'Insufficient data for stability analysis'}
        
        stability_metrics = {}
        
        # Calculate correlation stability for each pair
        kpi_columns = ['RTWP', 'SINR', 'PRB']
        available_columns = [col for col in kpi_columns if col in df.columns]
        
        for i, col1 in enumerate(available_columns):
            for j, col2 in enumerate(available_columns):
                if i < j:
                    rolling_corr = df[col1].rolling(window=window_size).corr(df[col2])
                    stability = self._calculate_correlation_stability(rolling_corr)
                    
                    stability_metrics[f"{col1}_{col2}"] = {
                        'stability_score': stability,
                        'stability_class': self._classify_stability(stability)
                    }
        
        return stability_metrics
    
    def _calculate_cross_correlations(self, df: pd.DataFrame) -> Dict:
        """Calculate cross-correlations with time lags"""
        cross_correlations = {}
        
        # RTWP vs SINR with different lags
        if 'RTWP' in df.columns and 'SINR' in df.columns:
            max_lag = min(10, len(df) // 4)
            rtwp_sinr_lags = {}
            
            for lag in range(-max_lag, max_lag + 1):
                if lag == 0:
                    continue
                
                if lag > 0:
                    # RTWP leads SINR
                    rtwp_shifted = df['RTWP'].shift(-lag)
                    sinr_original = df['SINR']
                else:
                    # SINR leads RTWP
                    rtwp_original = df['RTWP']
                    sinr_shifted = df['SINR'].shift(lag)
                
                # Calculate correlation for this lag
                if lag > 0:
                    corr = rtwp_shifted.corr(sinr_original)
                else:
                    corr = rtwp_original.corr(sinr_shifted)
                
                if not np.isnan(corr):
                    rtwp_sinr_lags[f"lag_{lag}"] = float(corr)
            
            # Find the lag with maximum correlation
            if rtwp_sinr_lags:
                best_lag = max(rtwp_sinr_lags.keys(), key=lambda k: abs(rtwp_sinr_lags[k]))
                cross_correlations['rtwp_sinr'] = {
                    'lags': rtwp_sinr_lags,
                    'best_lag': best_lag,
                    'max_correlation': rtwp_sinr_lags[best_lag]
                }
        
        return cross_correlations
    
    def _calculate_correlation_stability(self, rolling_corr: pd.Series) -> float:
        """Calculate stability score for rolling correlations"""
        if rolling_corr.empty or rolling_corr.std() == 0:
            return 1.0  # Perfect stability if no variation
        
        # Stability is inverse of coefficient of variation
        cv = rolling_corr.std() / abs(rolling_corr.mean()) if rolling_corr.mean() != 0 else float('inf')
        stability = 1.0 / (1.0 + cv)
        return float(stability)
    
    def _classify_correlation_strength(self, correlation: float) -> str:
        """Classify correlation strength"""
        if np.isnan(correlation):
            return 'no_correlation'
        
        abs_corr = abs(correlation)
        
        if abs_corr >= self.correlation_thresholds['strong_positive']:
            return 'strong_positive' if correlation > 0 else 'strong_negative'
        elif abs_corr >= self.correlation_thresholds['moderate_positive']:
            return 'moderate_positive' if correlation > 0 else 'moderate_negative'
        else:
            return 'weak'
    
    def _classify_stability(self, stability_score: float) -> str:
        """Classify correlation stability"""
        if stability_score >= 0.8:
            return 'highly_stable'
        elif stability_score >= 0.6:
            return 'moderately_stable'
        elif stability_score >= 0.4:
            return 'somewhat_unstable'
        else:
            return 'highly_unstable'
    
    def _generate_correlation_insights(self, results: Dict) -> List[str]:
        """Generate insights based on correlation analysis"""
        insights = []
        
        # Analyze pairwise correlations
        pairwise = results['pairwise_correlations']
        for pair, data in pairwise.items():
            if data['significance'] == 'significant':
                if data['strength'] in ['strong_positive', 'strong_negative']:
                    insights.append(
                        f"Strong {data['strength']} correlation between {pair.replace('_', ' and ')} "
                        f"(r={data['correlation']:.3f})"
                    )
                elif data['strength'] in ['moderate_positive', 'moderate_negative']:
                    insights.append(
                        f"Moderate {data['strength']} correlation between {pair.replace('_', ' and ')} "
                        f"(r={data['correlation']:.3f})"
                    )
        
        # Analyze correlation stability
        stability = results['correlation_stability']
        for pair, data in stability.items():
            if data['stability_class'] == 'highly_unstable':
                insights.append(
                    f"Highly unstable correlation between {pair.replace('_', ' and ')} "
                    f"- may indicate system issues"
                )
        
        # Analyze cross-correlations
        cross_corr = results['cross_correlations']
        for pair, data in cross_corr.items():
            if abs(data['max_correlation']) > 0.5:
                insights.append(
                    f"Strong cross-correlation between {pair.replace('_', ' and ')} "
                    f"with {data['best_lag']} time lag"
                )
        
        return insights
