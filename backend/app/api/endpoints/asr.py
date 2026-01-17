from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import tempfile
import os
from app.services.asr_service import ASRService
from app.services.clinical_report_service import ClinicalReportService
import json

router = APIRouter()

def get_asr_service():
    return ASRService()

def get_clinical_report_service():
    return ClinicalReportService()

class GenerateReportRequest(BaseModel):
    transcript: str
    patient_info: dict = None

@router.post("/transcribe-file")
async def transcribe_file(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file"""
    asr_service = get_asr_service()
    try:
        # Check if API key is configured
        if not asr_service.api_key:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "AssemblyAI API key not configured. Please add ASSEMBLYAI_API_KEY to your environment variables."}
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe the file
            result = await asr_service.transcribe_file(temp_file_path)
            print(f"ASR result: {result}")
            return JSONResponse(content={
                "success": True,
                "transcript": result['text'],
                "confidence": result['confidence'],
                "speakers": result['speakers']
            })
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
            
    except Exception as e:
        import traceback
        print(f"Transcription error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Transcription failed: {str(e)}"}
        )

@router.post("/generate-report")
async def generate_clinical_report(request: GenerateReportRequest):
    """Generate a clinical report from transcript"""
    clinical_report_service = get_clinical_report_service()
    try:
        if not request.transcript.strip():
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Transcript cannot be empty"}
            )
        
        # Generate comprehensive clinical report
        report = await clinical_report_service.generate_clinical_report(
            request.transcript, 
            request.patient_info
        )
        
        return JSONResponse(content={
            "success": True,
            "report": report
        })
        
    except Exception as e:
        import traceback
        print(f"Report generation error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Report generation failed: {str(e)}"}
        )

@router.websocket("/realtime-transcribe")
async def realtime_transcribe(websocket: WebSocket):
    """WebSocket endpoint for real-time transcription"""
    await websocket.accept()
    
    try:
        # Start real-time transcription
        async def on_transcript(text: str):
            await websocket.send_text(json.dumps({
                "type": "transcript",
                "text": text
            }))
        
        async def on_error(error: str):
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": error
            }))
        
        # This would need to be implemented with proper audio streaming
        # For now, just keep connection alive
        while True:
            data = await websocket.receive_text()
            # Handle incoming audio data here
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))
