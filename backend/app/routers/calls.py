from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.data import load_calls
from app.models import CallRecord, CallerType, Client, ResolutionStatus

router = APIRouter(prefix="/api/calls", tags=["calls"])


@router.get("", response_model=List[CallRecord])
def list_calls(
    client: Optional[Client] = None,
    caller_type: Optional[CallerType] = None,
    call_reason: Optional[str] = None,
    escalated_to_coordinator: Optional[bool] = None,
    resolution_status: Optional[ResolutionStatus] = None,
    caller_province: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    calls = load_calls()

    if client is not None:
        calls = [c for c in calls if c.client == client]
    if caller_type is not None:
        calls = [c for c in calls if c.caller_type == caller_type]
    if call_reason is not None:
        calls = [c for c in calls if c.call_reason == call_reason]
    if escalated_to_coordinator is not None:
        calls = [c for c in calls if c.escalated_to_coordinator == escalated_to_coordinator]
    if resolution_status is not None:
        calls = [c for c in calls if c.resolution_status == resolution_status]
    if caller_province is not None:
        calls = [c for c in calls if c.caller_province == caller_province]

    return calls[offset : offset + limit]


@router.get("/{call_id}", response_model=CallRecord)
def get_call(call_id: str):
    calls = load_calls()
    for call in calls:
        if call.call_id == call_id:
            return call
    raise HTTPException(status_code=404, detail=f"Call '{call_id}' not found")
