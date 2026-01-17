from typing import Dict, Any
import re
from datetime import datetime

class ClinicalReportService:
    def __init__(self):
        self.agent_service = None
        
    def _get_agent_service(self):
        if self.agent_service is None:
            from app.services.cloud_agent_service import CloudAgentService
            self.agent_service = CloudAgentService()
        return self.agent_service
        
    async def generate_clinical_report(self, transcript: str, patient_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a comprehensive clinical report from session transcript"""
        
        # Generate all sections concurrently for better performance
        sections = await self._generate_all_sections(transcript)
        
        # Create structured report
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "transcript_length": len(transcript.split()),
                "session_duration": self._estimate_session_duration(transcript)
            },
            "patient_presentation": sections["presentation"],
            "clinical_assessment": sections["assessment"], 
            "diagnostic_considerations": sections["diagnosis"],
            "risk_assessment": sections["risk"],
            "treatment_recommendations": sections["treatment"],
            "next_steps": sections["next_steps"]
        }
        
        return report
    
    async def _generate_all_sections(self, transcript: str) -> Dict[str, str]:
        """Generate all report sections using structured prompts"""
        
        base_prompt = f"""
        You are a clinical psychologist creating a CONCISE clinical report. 
        Use BULLET POINTS only. Be brief and highlight KEY findings.
        Limit each section to 3-5 bullet points maximum.
        
        TRANSCRIPT:
        {transcript}
        
        """
        
        sections = {}
        
        # Patient Presentation
        sections["presentation"] = self._get_section(base_prompt + """
        SECTION: PATIENT PRESENTATION (3-4 bullets max)
        • Chief complaint
        • Key symptoms with severity
        • Functional impact
        """)
        
        # Clinical Assessment  
        sections["assessment"] = self._get_section(base_prompt + """
        SECTION: CLINICAL ASSESSMENT (3-4 bullets max)
        • Mental status highlights
        • Mood/affect observations
        • Notable behaviors
        """)
        
        # Diagnostic Formulation
        sections["diagnosis"] = self._get_section(base_prompt + """
        SECTION: DIAGNOSTIC CONSIDERATIONS (2-3 bullets max)
        • Primary diagnostic possibility with DSM code
        • Key supporting criteria met
        """)
        
        # Risk Assessment
        sections["risk"] = self._get_section(base_prompt + """
        SECTION: RISK ASSESSMENT (2-3 bullets max)
        • Suicide/self-harm risk level
        • Safety concerns if any
        """)
        
        # Treatment Plan
        sections["treatment"] = self._get_section(base_prompt + """
        SECTION: TREATMENT RECOMMENDATIONS (3-4 bullets max)
        • Primary therapeutic approach
        • Immediate interventions
        • Follow-up frequency
        """)
        
        # Next Steps
        sections["next_steps"] = self._get_section(base_prompt + """
        SECTION: NEXT STEPS (2-3 bullets max)
        • Immediate actions needed
        • Referrals if indicated
        """)
        
        return sections
    
    def _get_section(self, prompt: str) -> str:
        """Get a specific section from the agent service"""
        agent_service = self._get_agent_service()
        response = agent_service.process_query(prompt)
        return response.get('response', 'Unable to generate this section')
    
    def _estimate_session_duration(self, transcript: str) -> str:
        """Estimate session duration based on transcript length"""
        word_count = len(transcript.split())
        # Assuming average speaking rate of 150 words per minute
        minutes = word_count / 150
        return f"~{int(minutes)} minutes"
