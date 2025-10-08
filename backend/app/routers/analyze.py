from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import io
import asyncio
from datetime import datetime

from ..db.session import get_db
from ..db.models import Upload, KPIData, AnalysisResult
from ..services.parser import KPIParser
from ..services.anomaly import AnomalyDetector
from ..services.correlation import CorrelationEngine
from ..services.ai_summary import AISummaryService
from ..utils.logger import analysis_logger, api_logger
from .auth import get_current_user

router = APIRouter(prefix="/analyze", tags=["analysis"])

# Initialize services
parser = KPIParser()
anomaly_detector = AnomalyDetector()
correlation_engine = CorrelationEngine()
ai_service = AISummaryService()

@router.post("/")
async def analyze_kpi_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze KPI data from uploaded CSV file
    
    Args:
        file: CSV file containing KPI data
        db: Database session
        
    Returns:
        Analysis results including AI summary
    """
    start_time = datetime.utcnow()
    
    try:
        # Log analysis start
        analysis_logger.log_analysis_start(
            filename=file.filename,
            file_size=file.size,
            user_id=current_user["user_id"]
        )
        
        # Validate file
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Read file content
        content = await file.read()
        
        # Create upload record
        upload_record = Upload(
            filename=file.filename,
            original_filename=file.filename,
            file_size=file.size,
            user_id=current_user["user_id"],
            status="processing"
        )
        db.add(upload_record)
        db.commit()
        db.refresh(upload_record)
        
        # Parse CSV data
        df, metadata = parser.parse_csv(content, file.filename)
        
        # Store KPI data
        kpi_records = []
        for _, row in df.iterrows():
            kpi_record = KPIData(
                upload_id=upload_record.id,
                timestamp=row['TIME'],
                rtwp=row.get('RTWP'),
                sinr=row.get('SINR'),
                prb=row.get('PRB')
            )
            kpi_records.append(kpi_record)
        
        db.bulk_save_objects(kpi_records)
        db.commit()
        
        # Calculate statistics
        kpi_stats = {
            'rtwp_mean': float(df['RTWP'].mean()) if 'RTWP' in df.columns else None,
            'rtwp_std': float(df['RTWP'].std()) if 'RTWP' in df.columns else None,
            'rtwp_min': float(df['RTWP'].min()) if 'RTWP' in df.columns else None,
            'rtwp_max': float(df['RTWP'].max()) if 'RTWP' in df.columns else None,
            'sinr_mean': float(df['SINR'].mean()) if 'SINR' in df.columns else None,
            'sinr_std': float(df['SINR'].std()) if 'SINR' in df.columns else None,
            'sinr_min': float(df['SINR'].min()) if 'SINR' in df.columns else None,
            'sinr_max': float(df['SINR'].max()) if 'SINR' in df.columns else None,
            'prb_mean': float(df['PRB'].mean()) if 'PRB' in df.columns else None,
            'prb_std': float(df['PRB'].std()) if 'PRB' in df.columns else None,
            'prb_min': float(df['PRB'].min()) if 'PRB' in df.columns else None,
            'prb_max': float(df['PRB'].max()) if 'PRB' in df.columns else None,
            'total_records': len(df)
        }
        
        # Detect anomalies
        anomaly_results = anomaly_detector.detect_anomalies(df)
        
        # Analyze correlations
        correlation_results = correlation_engine.analyze_correlations(df)
        
        # Generate AI summary
        ai_analysis = await ai_service.generate_analysis_summary(
            kpi_stats, anomaly_results, correlation_results, metadata
        )
        
        # Store analysis results
        analysis_record = AnalysisResult(
            upload_id=upload_record.id,
            rtwp_mean=kpi_stats['rtwp_mean'],
            rtwp_std=kpi_stats['rtwp_std'],
            sinr_mean=kpi_stats['sinr_mean'],
            sinr_std=kpi_stats['sinr_std'],
            prb_mean=kpi_stats['prb_mean'],
            prb_std=kpi_stats['prb_std'],
            rtwp_anomalies=anomaly_results['rtwp_anomalies']['count'],
            sinr_anomalies=anomaly_results['sinr_anomalies']['count'],
            prb_anomalies=anomaly_results['prb_anomalies']['count'],
            rtwp_sinr_correlation=correlation_results['pairwise_correlations'].get('RTWP_SINR', {}).get('correlation'),
            rtwp_prb_correlation=correlation_results['pairwise_correlations'].get('RTWP_PRB', {}).get('correlation'),
            sinr_prb_correlation=correlation_results['pairwise_correlations'].get('SINR_PRB', {}).get('correlation'),
            ai_summary=ai_analysis['summary'],
            ai_confidence=ai_analysis['confidence_score'],
            ai_diagnosis=ai_analysis.get('sections', {}).get('root_cause_analysis', '')
        )
        
        db.add(analysis_record)
        
        # Update upload status
        upload_record.status = "completed"
        db.commit()
        
        # Log analysis completion
        total_anomalies = anomaly_results['summary']['total_anomalies']
        analysis_logger.log_analysis_complete(
            filename=file.filename,
            records_processed=len(df),
            anomalies_found=total_anomalies,
            user_id="anonymous"
        )
        
        # Prepare response
        response_data = {
            "upload_id": upload_record.id,
            "filename": file.filename,
            "metadata": metadata,
            "kpi_statistics": kpi_stats,
            "anomaly_analysis": anomaly_results,
            "correlation_analysis": correlation_results,
            "ai_analysis": ai_analysis,
            "processing_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
        }
        
        return response_data
        
    except Exception as e:
        # Update upload status to failed
        if 'upload_record' in locals():
            upload_record.status = "failed"
            db.commit()
        
        # Log error
        analysis_logger.log_analysis_error(
            filename=file.filename,
            error=str(e),
            user_id="anonymous"
        )
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/{upload_id}")
async def get_analysis_results(
    upload_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get analysis results for a specific upload
    
    Args:
        upload_id: ID of the upload
        db: Database session
        
    Returns:
        Analysis results
    """
    try:
        # Get upload record
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Get analysis results
        analysis = db.query(AnalysisResult).filter(AnalysisResult.upload_id == upload_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        # Get KPI data
        kpi_data = db.query(KPIData).filter(KPIData.upload_id == upload_id).all()
        
        return {
            "upload": {
                "id": upload.id,
                "filename": upload.filename,
                "upload_timestamp": upload.upload_timestamp,
                "status": upload.status
            },
            "analysis": {
                "id": analysis.id,
                "analysis_timestamp": analysis.analysis_timestamp,
                "rtwp_mean": analysis.rtwp_mean,
                "rtwp_std": analysis.rtwp_std,
                "sinr_mean": analysis.sinr_mean,
                "sinr_std": analysis.sinr_std,
                "prb_mean": analysis.prb_mean,
                "prb_std": analysis.prb_std,
                "rtwp_anomalies": analysis.rtwp_anomalies,
                "sinr_anomalies": analysis.sinr_anomalies,
                "prb_anomalies": analysis.prb_anomalies,
                "rtwp_sinr_correlation": analysis.rtwp_sinr_correlation,
                "rtwp_prb_correlation": analysis.rtwp_prb_correlation,
                "sinr_prb_correlation": analysis.sinr_prb_correlation,
                "ai_summary": analysis.ai_summary,
                "ai_confidence": analysis.ai_confidence,
                "ai_diagnosis": analysis.ai_diagnosis
            },
            "kpi_data_count": len(kpi_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

@router.get("/")
async def list_analyses(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all analyses with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of analyses
    """
    try:
        # Get uploads with analysis results (filter by user unless admin)
        query = db.query(Upload).filter(Upload.status == "completed")
        
        # Non-admin users can only see their own uploads
        if current_user["role"] != "admin":
            query = query.filter(Upload.user_id == current_user["user_id"])
        
        uploads = query.offset(skip).limit(limit).all()
        
        analyses = []
        for upload in uploads:
            analysis = db.query(AnalysisResult).filter(AnalysisResult.upload_id == upload.id).first()
            if analysis:
                analyses.append({
                    "upload_id": upload.id,
                    "filename": upload.filename,
                    "upload_timestamp": upload.upload_timestamp,
                    "analysis_timestamp": analysis.analysis_timestamp,
                    "total_anomalies": analysis.rtwp_anomalies + analysis.sinr_anomalies + analysis.prb_anomalies,
                    "ai_confidence": analysis.ai_confidence
                })
        
        return {
            "analyses": analyses,
            "total": len(analyses),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing analyses: {str(e)}")
