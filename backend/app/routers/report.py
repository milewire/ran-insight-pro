from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Dict, Any
import pandas as pd
from datetime import datetime

from ..db.session import get_db
from ..db.models import Upload, KPIData, AnalysisResult
from ..services.report_gen import ReportGenerator
from ..services.parser import KPIParser
from ..utils.logger import api_logger

router = APIRouter(prefix="/report", tags=["reports"])

# Initialize services
report_generator = ReportGenerator()
parser = KPIParser()

@router.get("/pdf/{upload_id}")
async def generate_pdf_report(
    upload_id: int,
    db: Session = Depends(get_db)
) -> Response:
    """
    Generate PDF report for a specific analysis
    
    Args:
        upload_id: ID of the upload/analysis
        db: Database session
        
    Returns:
        PDF file response
    """
    try:
        # Get upload and analysis data
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        analysis = db.query(AnalysisResult).filter(AnalysisResult.upload_id == upload_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get KPI data
        kpi_data = db.query(KPIData).filter(KPIData.upload_id == upload_id).all()
        
        # Convert to DataFrame for report generation
        kpi_df = pd.DataFrame([{
            'TIME': kpi.timestamp,
            'RTWP': kpi.rtwp,
            'SINR': kpi.sinr,
            'PRB': kpi.prb
        } for kpi in kpi_data])
        
        # Prepare data for report
        kpi_stats = {
            'rtwp_mean': analysis.rtwp_mean,
            'rtwp_std': analysis.rtwp_std,
            'sinr_mean': analysis.sinr_mean,
            'sinr_std': analysis.sinr_std,
            'prb_mean': analysis.prb_mean,
            'prb_std': analysis.prb_std,
            'total_records': len(kpi_data)
        }
        
        # Create mock anomaly and correlation results for report
        anomaly_results = {
            'summary': {
                'total_anomalies': analysis.rtwp_anomalies + analysis.sinr_anomalies + analysis.prb_anomalies,
                'severity': 'medium'  # Default severity
            },
            'rtwp_anomalies': {'count': analysis.rtwp_anomalies},
            'sinr_anomalies': {'count': analysis.sinr_anomalies},
            'prb_anomalies': {'count': analysis.prb_anomalies}
        }
        
        correlation_results = {
            'pairwise_correlations': {
                'RTWP_SINR': {'correlation': analysis.rtwp_sinr_correlation or 0},
                'RTWP_PRB': {'correlation': analysis.rtwp_prb_correlation or 0},
                'SINR_PRB': {'correlation': analysis.sinr_prb_correlation or 0}
            }
        }
        
        ai_analysis = {
            'summary': analysis.ai_summary or 'No AI analysis available.',
            'confidence_score': analysis.ai_confidence or 0.5,
            'risk_level': 'medium',  # Default risk level
            'key_findings': [],
            'recommendations': []
        }
        
        metadata = {
            'filename': upload.filename,
            'total_records': len(kpi_data),
            'time_range': {
                'start': kpi_df['TIME'].min().isoformat() if not kpi_df.empty else None,
                'end': kpi_df['TIME'].max().isoformat() if not kpi_df.empty else None
            }
        }
        
        # Generate PDF report
        pdf_content = await report_generator.generate_analysis_report(
            kpi_df, kpi_stats, anomaly_results, correlation_results,
            ai_analysis, metadata, upload.filename
        )
        
        # Log report generation
        api_logger.log_request("GET", f"/report/pdf/{upload_id}")
        
        # Return PDF response
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=ran_analysis_report_{upload_id}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error("GET", f"/report/pdf/{upload_id}", str(e))
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/summary/{upload_id}")
async def get_report_summary(
    upload_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a summary of analysis results suitable for report generation
    
    Args:
        upload_id: ID of the upload/analysis
        db: Database session
        
    Returns:
        Report summary data
    """
    try:
        # Get upload and analysis data
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        analysis = db.query(AnalysisResult).filter(AnalysisResult.upload_id == upload_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get KPI data count
        kpi_count = db.query(KPIData).filter(KPIData.upload_id == upload_id).count()
        
        # Calculate total anomalies
        total_anomalies = analysis.rtwp_anomalies + analysis.sinr_anomalies + analysis.prb_anomalies
        
        # Determine risk level based on anomalies
        if total_anomalies > 50:
            risk_level = 'high'
        elif total_anomalies > 20:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Prepare summary
        summary = {
            "report_metadata": {
                "upload_id": upload_id,
                "filename": upload.filename,
                "upload_timestamp": upload.upload_timestamp,
                "analysis_timestamp": analysis.analysis_timestamp,
                "total_records": kpi_count
            },
            "kpi_summary": {
                "rtwp_mean": analysis.rtwp_mean,
                "rtwp_std": analysis.rtwp_std,
                "sinr_mean": analysis.sinr_mean,
                "sinr_std": analysis.sinr_std,
                "prb_mean": analysis.prb_mean,
                "prb_std": analysis.prb_std
            },
            "anomaly_summary": {
                "total_anomalies": total_anomalies,
                "rtwp_anomalies": analysis.rtwp_anomalies,
                "sinr_anomalies": analysis.sinr_anomalies,
                "prb_anomalies": analysis.prb_anomalies,
                "risk_level": risk_level
            },
            "correlation_summary": {
                "rtwp_sinr_correlation": analysis.rtwp_sinr_correlation,
                "rtwp_prb_correlation": analysis.rtwp_prb_correlation,
                "sinr_prb_correlation": analysis.sinr_prb_correlation
            },
            "ai_analysis": {
                "summary": analysis.ai_summary,
                "confidence_score": analysis.ai_confidence,
                "diagnosis": analysis.ai_diagnosis
            }
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error("GET", f"/report/summary/{upload_id}", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get report summary: {str(e)}")

@router.get("/list")
async def list_reports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all available reports with basic information
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of available reports
    """
    try:
        # Get uploads with completed analyses
        uploads = db.query(Upload).filter(Upload.status == "completed").offset(skip).limit(limit).all()
        
        reports = []
        for upload in uploads:
            analysis = db.query(AnalysisResult).filter(AnalysisResult.upload_id == upload.id).first()
            if analysis:
                total_anomalies = analysis.rtwp_anomalies + analysis.sinr_anomalies + analysis.prb_anomalies
                
                reports.append({
                    "upload_id": upload.id,
                    "filename": upload.filename,
                    "upload_timestamp": upload.upload_timestamp,
                    "analysis_timestamp": analysis.analysis_timestamp,
                    "total_anomalies": total_anomalies,
                    "ai_confidence": analysis.ai_confidence,
                    "has_ai_analysis": bool(analysis.ai_summary)
                })
        
        return {
            "reports": reports,
            "total": len(reports),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        api_logger.log_error("GET", "/report/list", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")

@router.delete("/{upload_id}")
async def delete_report(
    upload_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete a report and associated data
    
    Args:
        upload_id: ID of the upload/analysis to delete
        db: Database session
        
    Returns:
        Deletion confirmation
    """
    try:
        # Check if upload exists
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Delete associated data
        db.query(KPIData).filter(KPIData.upload_id == upload_id).delete()
        db.query(AnalysisResult).filter(AnalysisResult.upload_id == upload_id).delete()
        db.query(Upload).filter(Upload.id == upload_id).delete()
        
        db.commit()
        
        api_logger.log_request("DELETE", f"/report/{upload_id}")
        
        return {
            "message": f"Report {upload_id} deleted successfully",
            "upload_id": upload_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error("DELETE", f"/report/{upload_id}", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")
