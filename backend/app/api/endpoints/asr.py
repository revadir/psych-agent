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
        # Use AI service to generate actual clinical content
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
        import traceback
        print(f"Note generation error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Note generation failed: {str(e)}"}
        )
