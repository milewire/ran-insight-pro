from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel

from ..db.session import get_db
from ..db.models import FirmwareLog
from ..utils.logger import api_logger

router = APIRouter(prefix="/firmware", tags=["firmware"])

# Pydantic models for request/response
class FirmwareEntry(BaseModel):
    node_id: str
    ru_version: Optional[str] = None
    bb_version: Optional[str] = None
    firmware_date: Optional[datetime] = None
    notes: Optional[str] = None

class FirmwareUpdate(BaseModel):
    ru_version: Optional[str] = None
    bb_version: Optional[str] = None
    firmware_date: Optional[datetime] = None
    notes: Optional[str] = None

@router.get("/")
async def list_firmware_versions(
    node_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List firmware versions with optional filtering
    
    Args:
        node_id: Optional node ID filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of firmware versions
    """
    try:
        query = db.query(FirmwareLog)
        
        if node_id:
            query = query.filter(FirmwareLog.node_id == node_id)
        
        firmware_entries = query.offset(skip).limit(limit).all()
        
        results = []
        for entry in firmware_entries:
            results.append({
                "id": entry.id,
                "node_id": entry.node_id,
                "ru_version": entry.ru_version,
                "bb_version": entry.bb_version,
                "firmware_date": entry.firmware_date,
                "log_timestamp": entry.log_timestamp,
                "is_valid": entry.is_valid,
                "notes": entry.notes
            })
        
        api_logger.log_request("GET", "/firmware")
        
        return {
            "firmware_entries": results,
            "total": len(results),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        api_logger.log_error("GET", "/firmware", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list firmware versions: {str(e)}")

@router.post("/")
async def log_firmware_version(
    firmware_entry: FirmwareEntry,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Log a new firmware version entry
    
    Args:
        firmware_entry: Firmware version data
        db: Database session
        
    Returns:
        Created firmware entry
    """
    try:
        # Create new firmware log entry
        new_entry = FirmwareLog(
            node_id=firmware_entry.node_id,
            ru_version=firmware_entry.ru_version,
            bb_version=firmware_entry.bb_version,
            firmware_date=firmware_entry.firmware_date,
            notes=firmware_entry.notes
        )
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        api_logger.log_request("POST", "/firmware")
        
        return {
            "id": new_entry.id,
            "node_id": new_entry.node_id,
            "ru_version": new_entry.ru_version,
            "bb_version": new_entry.bb_version,
            "firmware_date": new_entry.firmware_date,
            "log_timestamp": new_entry.log_timestamp,
            "is_valid": new_entry.is_valid,
            "notes": new_entry.notes,
            "message": "Firmware version logged successfully"
        }
        
    except Exception as e:
        api_logger.log_error("POST", "/firmware", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to log firmware version: {str(e)}")

@router.get("/{entry_id}")
async def get_firmware_entry(
    entry_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific firmware entry by ID
    
    Args:
        entry_id: ID of the firmware entry
        db: Database session
        
    Returns:
        Firmware entry details
    """
    try:
        entry = db.query(FirmwareLog).filter(FirmwareLog.id == entry_id).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Firmware entry not found")
        
        api_logger.log_request("GET", f"/firmware/{entry_id}")
        
        return {
            "id": entry.id,
            "node_id": entry.node_id,
            "ru_version": entry.ru_version,
            "bb_version": entry.bb_version,
            "firmware_date": entry.firmware_date,
            "log_timestamp": entry.log_timestamp,
            "is_valid": entry.is_valid,
            "notes": entry.notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error("GET", f"/firmware/{entry_id}", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get firmware entry: {str(e)}")

@router.put("/{entry_id}")
async def update_firmware_entry(
    entry_id: int,
    firmware_update: FirmwareUpdate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update a firmware entry
    
    Args:
        entry_id: ID of the firmware entry to update
        firmware_update: Updated firmware data
        db: Database session
        
    Returns:
        Updated firmware entry
    """
    try:
        entry = db.query(FirmwareLog).filter(FirmwareLog.id == entry_id).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Firmware entry not found")
        
        # Update fields if provided
        if firmware_update.ru_version is not None:
            entry.ru_version = firmware_update.ru_version
        if firmware_update.bb_version is not None:
            entry.bb_version = firmware_update.bb_version
        if firmware_update.firmware_date is not None:
            entry.firmware_date = firmware_update.firmware_date
        if firmware_update.notes is not None:
            entry.notes = firmware_update.notes
        
        db.commit()
        db.refresh(entry)
        
        api_logger.log_request("PUT", f"/firmware/{entry_id}")
        
        return {
            "id": entry.id,
            "node_id": entry.node_id,
            "ru_version": entry.ru_version,
            "bb_version": entry.bb_version,
            "firmware_date": entry.firmware_date,
            "log_timestamp": entry.log_timestamp,
            "is_valid": entry.is_valid,
            "notes": entry.notes,
            "message": "Firmware entry updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error("PUT", f"/firmware/{entry_id}", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update firmware entry: {str(e)}")

@router.delete("/{entry_id}")
async def delete_firmware_entry(
    entry_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete a firmware entry
    
    Args:
        entry_id: ID of the firmware entry to delete
        db: Database session
        
    Returns:
        Deletion confirmation
    """
    try:
        entry = db.query(FirmwareLog).filter(FirmwareLog.id == entry_id).first()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Firmware entry not found")
        
        db.delete(entry)
        db.commit()
        
        api_logger.log_request("DELETE", f"/firmware/{entry_id}")
        
        return {
            "message": f"Firmware entry {entry_id} deleted successfully",
            "entry_id": entry_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error("DELETE", f"/firmware/{entry_id}", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete firmware entry: {str(e)}")

@router.get("/node/{node_id}/history")
async def get_node_firmware_history(
    node_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get firmware history for a specific node
    
    Args:
        node_id: Node ID to get history for
        db: Database session
        
    Returns:
        Firmware history for the node
    """
    try:
        entries = db.query(FirmwareLog).filter(
            FirmwareLog.node_id == node_id
        ).order_by(FirmwareLog.log_timestamp.desc()).all()
        
        if not entries:
            raise HTTPException(status_code=404, detail=f"No firmware history found for node {node_id}")
        
        history = []
        for entry in entries:
            history.append({
                "id": entry.id,
                "ru_version": entry.ru_version,
                "bb_version": entry.bb_version,
                "firmware_date": entry.firmware_date,
                "log_timestamp": entry.log_timestamp,
                "is_valid": entry.is_valid,
                "notes": entry.notes
            })
        
        # Get current firmware (most recent valid entry)
        current_firmware = None
        for entry in entries:
            if entry.is_valid:
                current_firmware = {
                    "ru_version": entry.ru_version,
                    "bb_version": entry.bb_version,
                    "firmware_date": entry.firmware_date
                }
                break
        
        api_logger.log_request("GET", f"/firmware/node/{node_id}/history")
        
        return {
            "node_id": node_id,
            "current_firmware": current_firmware,
            "history": history,
            "total_entries": len(history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.log_error("GET", f"/firmware/node/{node_id}/history", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get firmware history: {str(e)}")

@router.post("/validate")
async def validate_firmware_versions(
    node_ids: List[str],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Validate firmware versions for multiple nodes
    
    Args:
        node_ids: List of node IDs to validate
        db: Database session
        
    Returns:
        Validation results
    """
    try:
        validation_results = []
        
        for node_id in node_ids:
            # Get latest firmware entry for the node
            latest_entry = db.query(FirmwareLog).filter(
                FirmwareLog.node_id == node_id
            ).order_by(FirmwareLog.log_timestamp.desc()).first()
            
            if latest_entry:
                # Basic validation logic (can be enhanced)
                is_valid = (
                    latest_entry.ru_version is not None and
                    latest_entry.bb_version is not None and
                    latest_entry.firmware_date is not None
                )
                
                validation_results.append({
                    "node_id": node_id,
                    "ru_version": latest_entry.ru_version,
                    "bb_version": latest_entry.bb_version,
                    "firmware_date": latest_entry.firmware_date,
                    "is_valid": is_valid,
                    "validation_timestamp": datetime.utcnow().isoformat()
                })
            else:
                validation_results.append({
                    "node_id": node_id,
                    "ru_version": None,
                    "bb_version": None,
                    "firmware_date": None,
                    "is_valid": False,
                    "validation_timestamp": datetime.utcnow().isoformat(),
                    "error": "No firmware data found"
                })
        
        api_logger.log_request("POST", "/firmware/validate")
        
        return {
            "validation_results": validation_results,
            "total_nodes": len(node_ids),
            "valid_nodes": sum(1 for r in validation_results if r["is_valid"]),
            "invalid_nodes": sum(1 for r in validation_results if not r["is_valid"])
        }
        
    except Exception as e:
        api_logger.log_error("POST", "/firmware/validate", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to validate firmware versions: {str(e)}")
