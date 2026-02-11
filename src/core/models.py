from pydantic import BaseModel, Field
from typing import List, Optional

class Lead(BaseModel):
    name: str
    title: str
    company: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    triggers: List[str] = Field(default_factory=list)
    persona_profile: Optional[dict] = Field(default_factory=dict)

class Hypothesis(BaseModel):
    name: str = "Generic Hypothesis"
    description: str = "Test a specific messaging angle."
    experiment_variant: str # "Scenario A" or "Scenario B"

class Message(BaseModel):
    content: str
    subject_line: Optional[str] = None
    variant_type: str # 'A', 'B', 'Control'
    reasoning: str # Why this message was generated
    lead_id: str # Link back to prospect (or name for simple lookup)

class ExperimentResult(BaseModel):
    lead_id: str
    variant_chosen: str
    sent: bool = True
    opened: bool = False
    replied: bool = False
    meeting_booked: bool = False
    
class Experiment(BaseModel):
    name: str
    variant_a_hypothesis: Hypothesis
    variant_b_hypothesis: Hypothesis
    leads: List[Lead] = Field(default_factory=list)
    results: List[ExperimentResult] = Field(default_factory=list)
