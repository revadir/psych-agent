from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.clinical_report_service import ClinicalReportService
from app.api.auth import get_current_user
from app.models.database import User

router = APIRouter()
report_service = ClinicalReportService()

class ReportRequest(BaseModel):
    transcript: str

@router.post("/generate-clinical-report")
async def generate_clinical_report(
    request: ReportRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a clinical report from session transcript"""
    try:
        if not request.transcript.strip():
            raise HTTPException(status_code=400, detail="Transcript cannot be empty")
        
        report = await report_service.generate_clinical_report(request.transcript)
        
        return JSONResponse(content={
            "success": True,
            "report": report
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
