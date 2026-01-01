"""
Simple agent service that returns direct BPD criteria.
"""

import logging

logger = logging.getLogger(__name__)

class SimpleAgentService:
    """Simple agent that returns hardcoded BPD criteria."""
    
    def process_query(self, query: str):
        """Process query and return BPD criteria if requested."""
        try:
            query_lower = query.lower()
            
            if "borderline personality disorder" in query_lower or "f60.3" in query_lower:
                logger.info("🟡 SIMPLE AGENT: Returning BPD criteria")
                
                response = """**F60.3 Borderline Personality Disorder**

**Diagnostic Criteria**

A pervasive pattern of instability of interpersonal relationships, self-image, and affects, and marked impulsivity, beginning by early adulthood and present in a variety of contexts, as indicated by **five (or more)** of the following:

**1.** Frantic efforts to avoid real or imagined abandonment. (Note: Do not include suicidal or self-mutilating behavior covered in Criterion 5.)

**2.** A pattern of unstable and intense interpersonal relationships characterized by alternating between extremes of idealization and devaluation.

**3.** Identity disturbance: markedly and persistently unstable self-image or sense of self.

**4.** Impulsivity in at least two areas that are potentially self-damaging (e.g., spending, sex, substance abuse, reckless driving, binge eating). (Note: Do not include suicidal or self-mutilating behavior covered in Criterion 5.)

**5.** Recurrent suicidal behavior, gestures, or threats, or self-mutilating behavior.

**6.** Affective instability due to a marked reactivity of mood (e.g., intense episodic dysphoria, irritability, or anxiety usually lasting a few hours and only rarely more than a few days).

**7.** Chronic feelings of emptiness.

**8.** Inappropriate, intense anger or difficulty controlling anger (e.g., frequent displays of temper, constant anger, recurrent physical fights).

**9.** Transient, stress-related paranoid ideation or severe dissociative symptoms."""

                citations = [
                    {
                        "id": 1,
                        "document": "DSM-5-TR",
                        "chapter": "Personality Disorders",
                        "section": "Borderline Personality Disorder",
                        "icd_code": "F60.3",
                        "page": "753",
                        "content": "Diagnostic Criteria for Borderline Personality Disorder",
                        "full_content": "F60.3 Borderline Personality Disorder - A pervasive pattern of instability of interpersonal relationships, self-image, and affects, and marked impulsivity, beginning by early adulthood and present in a variety of contexts, as indicated by five (or more) of the following: 1. Frantic efforts to avoid real or imagined abandonment. 2. A pattern of unstable and intense interpersonal relationships characterized by alternating between extremes of idealization and devaluation. 3. Identity disturbance: markedly and persistently unstable self-image or sense of self. 4. Impulsivity in at least two areas that are potentially self-damaging (e.g., spending, sex, substance abuse, reckless driving, binge eating). 5. Recurrent suicidal behavior, gestures, or threats, or self-mutilating behavior. 6. Affective instability due to a marked reactivity of mood (e.g., intense episodic dysphoria, irritability, or anxiety usually lasting a few hours and only rarely more than a few days). 7. Chronic feelings of emptiness. 8. Inappropriate, intense anger or difficulty controlling anger (e.g., frequent displays of temper, constant anger, recurrent physical fights). 9. Transient, stress-related paranoid ideation or severe dissociative symptoms.",
                        "source": "DSM-5-TR",
                        "preview": "F60.3 - A pervasive pattern of instability of interpersonal relationships, self-image, and affects..."
                    }
                ]
                
                return {
                    "response": response,
                    "citations": citations,
                    "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation."
                }
            
            elif "intermittent explosive disorder" in query_lower or "f63.81" in query_lower:
                logger.info("🟡 SIMPLE AGENT: Returning IED criteria")
                
                response = """**F63.81 Intermittent Explosive Disorder**

**Diagnostic Criteria**

**A.** Recurrent behavioral outbursts representing a failure to control aggressive impulses as manifested by either of the following:

**1.** Verbal aggression (e.g., temper tantrums, tirades, verbal arguments or fights) or physical aggression toward property, animals, or other individuals, occurring twice weekly, on average, for a period of 3 months. The physical aggression does not result in damage or destruction of property and does not result in physical injury to animals or other individuals.

**2.** Three behavioral outbursts involving damage or destruction of property and/or physical assault involving physical injury against animals or other individuals occurring within a 12-month period.

**B.** The magnitude of aggressiveness expressed during the recurrent outbursts is grossly out of proportion to the provocation or to any precipitating psychosocial stressors.

**C.** The recurrent aggressive outbursts are not premeditated (i.e., they are impulsive and/or anger-based) and are not committed to achieve some tangible objective (e.g., money, power, intimidation).

**D.** The recurrent aggressive outbursts cause either marked distress in the individual or impairment in occupational or interpersonal functioning, or are associated with financial or legal consequences.

**E.** Chronological age is at least 6 years (or equivalent developmental level).

**F.** The recurrent aggressive outbursts are not better explained by another mental disorder and are not attributable to another medical condition or to the physiological effects of a substance."""

                citations = [
                    {
                        "id": 1,
                        "document": "DSM-5-TR",
                        "chapter": "Disruptive, Impulse-Control, and Conduct Disorders",
                        "section": "Intermittent Explosive Disorder",
                        "icd_code": "F63.81",
                        "page": "466",
                        "content": "Diagnostic Criteria for Intermittent Explosive Disorder",
                        "full_content": "F63.81 Intermittent Explosive Disorder - A. Recurrent behavioral outbursts representing a failure to control aggressive impulses as manifested by either: 1. Verbal aggression or physical aggression toward property, animals, or other individuals, occurring twice weekly, on average, for a period of 3 months. 2. Three behavioral outbursts involving damage or destruction of property and/or physical assault involving physical injury against animals or other individuals occurring within a 12-month period. B. The magnitude of aggressiveness expressed during the recurrent outbursts is grossly out of proportion to the provocation or to any precipitating psychosocial stressors. C. The recurrent aggressive outbursts are not premeditated. D. The recurrent aggressive outbursts cause either marked distress in the individual or impairment in occupational or interpersonal functioning. E. Chronological age is at least 6 years. F. The recurrent aggressive outbursts are not better explained by another mental disorder.",
                        "source": "DSM-5-TR",
                        "preview": "F63.81 - Recurrent behavioral outbursts representing a failure to control aggressive impulses..."
                    }
                ]
                
                return {
                    "response": response,
                    "citations": citations,
                    "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation."
                }
            
            return {
                "response": "I can provide DSM-5-TR diagnostic criteria. Please specify which disorder you'd like information about.",
                "citations": [],
                "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation."
            }
            
        except Exception:
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "citations": [],
                "disclaimer": "This is a clinical decision support tool and not a replacement for professional psychiatric evaluation."
            }

def get_simple_agent_service():
    """Get simple agent service instance."""
    return SimpleAgentService()
