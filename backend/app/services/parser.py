import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import io

logger = logging.getLogger(__name__)

class KPIParser:
    """Handles parsing and cleaning of KPI data from CSV files"""
    
    def __init__(self):
        self.required_columns = ['RTWP', 'SINR', 'PRB']
        self.time_columns = ['TIME', 'TIMESTAMP', 'DATE', 'DATETIME']
    
    def parse_csv(self, file_content: bytes, filename: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Parse CSV file and return cleaned DataFrame with metadata
        
        Args:
            file_content: Raw file content as bytes
            filename: Original filename
            
        Returns:
            Tuple of (cleaned_dataframe, metadata_dict)
        """
        try:
            # Read CSV with flexible parsing
            df = pd.read_csv(
                io.StringIO(file_content.decode('utf-8')),
                encoding='utf-8',
                on_bad_lines='skip'
            )
            
            # Clean and standardize column names
            df = self._clean_headers(df)
            
            # Validate required columns
            missing_cols = self._validate_columns(df)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Process time column
            df = self._process_time_column(df)
            
            # Clean and validate data
            df = self._clean_data(df)
            
            # Generate metadata
            metadata = self._generate_metadata(df, filename)
            
            logger.info(f"Successfully parsed {len(df)} records from {filename}")
            return df, metadata
            
        except Exception as e:
            logger.error(f"Error parsing CSV file {filename}: {str(e)}")
            raise
    
    def _clean_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize column headers"""
        # Remove whitespace and convert to uppercase
        df.columns = df.columns.str.strip().str.upper()
        
        # Handle common column name variations
        column_mapping = {
            'RTWP_DBM': 'RTWP',
            'SINR_DB': 'SINR',
            'PRB_UTILIZATION': 'PRB',
            'PRB_UTIL': 'PRB',
            'PRB_USAGE': 'PRB',
            'TIMESTAMP': 'TIME',
            'DATETIME': 'TIME',
            'DATE': 'TIME'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        return df
    
    def _validate_columns(self, df: pd.DataFrame) -> List[str]:
        """Check for required columns and return missing ones"""
        missing = []
        for col in self.required_columns:
            if col not in df.columns:
                missing.append(col)
        return missing
    
    def _process_time_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and standardize time column"""
        time_col = None
        
        # Find time column
        for col in self.time_columns:
            if col in df.columns:
                time_col = col
                break
        
        if time_col is None:
            # Create synthetic time column if none exists
            df['TIME'] = pd.date_range(
                start='2024-01-01 00:00:00',
                periods=len(df),
                freq='15min'
            )
        else:
            # Convert to datetime
            try:
                df['TIME'] = pd.to_datetime(df[time_col], errors='coerce')
                # Drop original time column if it's different
                if time_col != 'TIME':
                    df.drop(columns=[time_col], inplace=True)
            except Exception as e:
                logger.warning(f"Could not parse time column {time_col}: {e}")
                # Create synthetic time column as fallback
                df['TIME'] = pd.date_range(
                    start='2024-01-01 00:00:00',
                    periods=len(df),
                    freq='15min'
                )
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate KPI data"""
        # Remove rows with all NaN values
        df = df.dropna(how='all')
        
        # Handle missing values in KPI columns
        for col in self.required_columns:
            if col in df.columns:
                # Replace NaN with median value
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                
                # Remove outliers (values beyond 3 standard deviations)
                mean_val = df[col].mean()
                std_val = df[col].std()
                if std_val > 0:
                    df = df[abs(df[col] - mean_val) <= 3 * std_val]
        
        # Ensure numeric types
        for col in self.required_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Sort by time
        df = df.sort_values('TIME').reset_index(drop=True)
        
        return df
    
    def _generate_metadata(self, df: pd.DataFrame, filename: str) -> Dict:
        """Generate metadata about the parsed data"""
        metadata = {
            'filename': filename,
            'total_records': len(df),
            'time_range': {
                'start': df['TIME'].min().isoformat() if not df.empty else None,
                'end': df['TIME'].max().isoformat() if not df.empty else None
            },
            'columns': list(df.columns),
            'data_quality': {
                'rtwp_missing': df['RTWP'].isna().sum() if 'RTWP' in df.columns else 0,
                'sinr_missing': df['SINR'].isna().sum() if 'SINR' in df.columns else 0,
                'prb_missing': df['PRB'].isna().sum() if 'PRB' in df.columns else 0
            },
            'statistics': {
                'rtwp_mean': float(df['RTWP'].mean()) if 'RTWP' in df.columns else None,
                'sinr_mean': float(df['SINR'].mean()) if 'SINR' in df.columns else None,
                'prb_mean': float(df['PRB'].mean()) if 'PRB' in df.columns else None
            }
        }
        
        return metadata
