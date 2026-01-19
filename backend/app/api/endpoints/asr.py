from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import os
from app.services.asr_service import ASRService

router = APIRouter()

def get_asr_service():
    return ASRService()

class GenerateNoteRequest(BaseModel):
    transcript: str
    patient_name: str
    note_template: str

@router.post("/transcribe-file")
async def transcribe_file(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file"""
    asr_service = get_asr_service()
    try:
        if not asr_service.api_key:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "AssemblyAI API key not configured"}
            )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            result = await asr_service.transcribe_file(temp_file_path)
            return JSONResponse(content={
                "success": True,
                "transcript": result['text'],
                "confidence": result['confidence'],
                "speakers": result['speakers']
            })
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        import traceback
        print(f"Transcription error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Transcription failed: {str(e)}"}
        )

@router.post("/generate-note")
async def generate_clinical_note(request: GenerateNoteRequest):
    """Generate a clinical note from transcript"""
    try:
        # Mock note generation - replace with actual AI service
        note_content = {
            "chief_complaint": f"Patient {request.patient_name} presents for {request.note_template.lower()}.",
            "history_present_illness": "Based on session transcript analysis...",
            "review_systems": "Patient reports relevant symptoms as discussed.",
            "assessment_plan": "Clinical assessment based on session content.",
            "followup_disposition": "Follow-up recommendations provided."
        }
        
        return JSONResponse(content={
            "success": True,
            "note": note_content
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Note generation failed: {str(e)}"}
        )
