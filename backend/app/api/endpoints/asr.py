from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import tempfile
import os
from app.services.asr_service import ASRService
from app.services.scribe_session_service import ScribeSessionService
from app.core.auth import get_current_user
from app.db.session import get_db
from app.models import User

router = APIRouter()

@router.get("/test")
async def test_asr():
    """Test ASR router is working"""
    return {"status": "ASR router working"}

def get_asr_service():
    return ASRService()

class GenerateNoteRequest(BaseModel):
    transcript: str
    patient_name: str
    note_template: str

class CreateScribeSessionRequest(BaseModel):
    patient_name: str
    patient_id: str
    note_template: str
    duration: str
    content: dict

@router.post("/transcribe-file")
async def transcribe_file(file: UploadFile = File(...)):
    """Transcribe an uploaded audio file"""
    print(f"🔍 ASR transcribe endpoint called with file: {file.filename}")
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
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Transcription failed: {str(e)}"}
        )

@router.post("/generate-note")
async def generate_clinical_note(request: GenerateNoteRequest):
    """Generate a clinical note from transcript"""
    try:
        # Lazy import to avoid startup delays
        from app.services.cloud_agent_service import CloudAgentService
        agent_service = CloudAgentService()
        
        # Generate each section using AI
        base_prompt = f"""
        You are a clinical psychologist generating a structured clinical note from this session transcript.
        Patient Name: {request.patient_name}
        Note Type: {request.note_template}
        
        TRANSCRIPT:
        {request.transcript}
        
        Generate the following section in 2-3 sentences, be concise and clinical:
        """
        
        # Generate Chief Complaint
        cc_response = agent_service.process_query(base_prompt + "CHIEF COMPLAINT: What is the patient's main concern or reason for visit?")
        chief_complaint = cc_response.get('response', 'Patient presents for clinical evaluation.')
        
        # Generate History of Present Illness
        hpi_response = agent_service.process_query(base_prompt + "HISTORY OF PRESENT ILLNESS: Describe the onset, duration, and characteristics of current symptoms.")
        history_present_illness = hpi_response.get('response', 'Patient describes current symptoms and their progression.')
        
        # Generate Review of Systems
        ros_response = agent_service.process_query(base_prompt + "REVIEW OF SYSTEMS: Summarize relevant positive and negative findings from systems review.")
        review_systems = ros_response.get('response', 'Review of systems notable for reported symptoms.')
        
        # Generate Assessment and Plan
        ap_response = agent_service.process_query(base_prompt + "ASSESSMENT AND PLAN: Provide clinical assessment with potential diagnoses and treatment recommendations.")
        assessment_plan = ap_response.get('response', 'Clinical assessment and treatment plan to be determined.')
        
        # Generate Follow-up
        fu_response = agent_service.process_query(base_prompt + "FOLLOW-UP/DISPOSITION: Recommend next steps, follow-up timeline, and any immediate actions needed.")
        followup_disposition = fu_response.get('response', 'Follow-up recommendations to be provided.')
        
        note_content = {
            "chief_complaint": chief_complaint,
            "history_present_illness": history_present_illness,
            "review_systems": review_systems,
            "assessment_plan": assessment_plan,
            "followup_disposition": followup_disposition
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

@router.post("/scribe-sessions")
async def create_scribe_session(
    request: CreateScribeSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new scribe session in database"""
    try:
        session = ScribeSessionService.create_session(
            db=db,
            user_id=current_user.id,
            patient_name=request.patient_name,
            patient_id=request.patient_id,
            note_template=request.note_template,
            duration=request.duration,
            content=request.content
        )
        
        return JSONResponse(content={
            "success": True,
            "session": {
                "id": session.id,
                "patient_id": session.patient_id,
                "patient_name": session.patient_name,
                "date": session.created_at.isoformat(),
                "duration": session.duration,
                "content": {
                    "chiefComplaint": session.chief_complaint,
                    "historyOfPresentIllness": session.history_present_illness,
                    "reviewOfSystems": session.review_systems,
                    "assessmentAndPlan": session.assessment_plan,
                    "followUpDisposition": session.followup_disposition
                }
            }
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Failed to create session: {str(e)}"}
        )

@router.get("/scribe-sessions")
async def get_scribe_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all scribe sessions for current user"""
    try:
        sessions = ScribeSessionService.get_user_sessions(db, current_user.id)
        
        return JSONResponse(content={
            "success": True,
            "sessions": [
                {
                    "id": session.id,
                    "patient_id": session.patient_id,
                    "patient_name": session.patient_name,
                    "date": session.created_at.isoformat(),
                    "duration": session.duration,
                    "content": {
                        "chiefComplaint": session.chief_complaint,
                        "historyOfPresentIllness": session.history_present_illness,
                        "reviewOfSystems": session.review_systems,
                        "assessmentAndPlan": session.assessment_plan,
                        "followUpDisposition": session.followup_disposition
                    }
                }
                for session in sessions
            ]
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Failed to get sessions: {str(e)}"}
        )

@router.delete("/scribe-sessions/{session_id}")
async def delete_scribe_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a scribe session"""
    try:
        deleted = ScribeSessionService.delete_session(db, session_id, current_user.id)
        
        if deleted:
            return JSONResponse(content={"success": True})
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Failed to delete session: {str(e)}"}
        )
