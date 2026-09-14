from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel

CallerType = Literal["plan_member", "provider"]
ResolutionStatus = Literal["resolved", "unresolved", "transferred"]
Client = Literal["GreenShield", "RBC Insurance", "Wawanesa", "Victor Insurance", "Entente"]
EscalationRisk = Literal["low", "medium", "high"]


class TranscriptTurn(BaseModel):
    speaker: Literal["Agent", "Caller"]
    text: str


class CallRecord(BaseModel):
    call_id: str
    timestamp: datetime
    duration_seconds: int
    caller_type: CallerType
    client: Client
    call_reason: str
    escalated_to_coordinator: bool
    escalation_notes: Optional[str] = None
    agent_id: str
    caller_province: str
    resolution_status: ResolutionStatus
    transcript: List[TranscriptTurn]
    sentiment_score: Optional[float] = None
    complexity_score: Optional[float] = None
    escalation_risk_flag: Optional[EscalationRisk] = None
