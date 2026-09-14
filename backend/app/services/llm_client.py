import json
import os
from typing import List, Literal

from pydantic import BaseModel, ValidationError

from app.models import TranscriptTurn

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = (
    "You are analyzing a contact center call transcript for a Canadian health and dental "
    "benefits provider. Read the transcript and the logged call reason, then respond with "
    "ONLY a JSON object (no prose, no markdown fences) with exactly these fields:\n"
    '{"sentiment_score": <float from -1.0 (very negative) to 1.0 (very positive), reflecting '
    'the caller\'s emotional tone>, "complexity_score": <float from 0.0 (trivial, routine) to '
    '10.0 (highly complex, multi-step, ambiguous)>, "escalation_risk_flag": <one of "low", '
    '"medium", "high", estimating the risk this caller escalates further or calls back '
    'unresolved>}'
)


class TranscriptAnalysis(BaseModel):
    sentiment_score: float
    complexity_score: float
    escalation_risk_flag: Literal["low", "medium", "high"]


class LLMNotConfiguredError(RuntimeError):
    pass


class LLMResponseError(RuntimeError):
    pass


def _format_transcript(transcript: List[TranscriptTurn]) -> str:
    return "\n".join(f"{turn.speaker}: {turn.text}" for turn in transcript)


def _build_user_message(transcript: List[TranscriptTurn], call_reason: str, escalated: bool) -> str:
    return (
        f"Call reason (agent-logged): {call_reason}\n"
        f"Escalated to coordinator: {escalated}\n\n"
        f"Transcript:\n{_format_transcript(transcript)}"
    )


def _get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMNotConfiguredError(
            "ANTHROPIC_API_KEY is not set. Set it in the environment before running the "
            "transcript analysis pipeline."
        )
    try:
        import anthropic
    except ImportError as exc:
        raise LLMNotConfiguredError(
            "The 'anthropic' package is not installed. Run: pip install anthropic"
        ) from exc
    return anthropic.Anthropic(api_key=api_key)


def parse_analysis_response(raw_text: str) -> TranscriptAnalysis:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise LLMResponseError(f"Model did not return valid JSON: {raw_text!r}") from exc

    try:
        return TranscriptAnalysis.model_validate(data)
    except ValidationError as exc:
        raise LLMResponseError(f"Model JSON did not match expected schema: {data!r}") from exc


def analyze_transcript(
    transcript: List[TranscriptTurn], call_reason: str, escalated: bool = False
) -> TranscriptAnalysis:
    client = _get_client()
    message = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_message(transcript, call_reason, escalated)}],
    )
    raw_text = message.content[0].text
    return parse_analysis_response(raw_text)
