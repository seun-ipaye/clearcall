from collections import Counter, defaultdict
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.data import load_calls

router = APIRouter(prefix="/api/stats", tags=["stats"])


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


class OverviewStats(BaseModel):
    total_calls: int
    avg_handle_time_seconds: float
    escalation_rate: float
    resolution_rate: float


@router.get("/overview", response_model=OverviewStats)
def overview():
    calls = load_calls()
    total = len(calls)
    escalated = sum(1 for c in calls if c.escalated_to_coordinator)
    resolved = sum(1 for c in calls if c.resolution_status == "resolved")
    avg_handle_time = sum(c.duration_seconds for c in calls) / total if total else 0.0

    return OverviewStats(
        total_calls=total,
        avg_handle_time_seconds=round(avg_handle_time, 1),
        escalation_rate=_rate(escalated, total),
        resolution_rate=_rate(resolved, total),
    )


class ReasonStats(BaseModel):
    call_reason: str
    count: int
    avg_duration_seconds: float
    escalation_rate: float
    resolution_rate: float


@router.get("/by-reason", response_model=List[ReasonStats])
def by_reason():
    calls = load_calls()
    grouped: dict[str, list] = defaultdict(list)
    for c in calls:
        grouped[c.call_reason].append(c)

    results = []
    for reason, group in grouped.items():
        count = len(group)
        escalated = sum(1 for c in group if c.escalated_to_coordinator)
        resolved = sum(1 for c in group if c.resolution_status == "resolved")
        avg_duration = sum(c.duration_seconds for c in group) / count
        results.append(
            ReasonStats(
                call_reason=reason,
                count=count,
                avg_duration_seconds=round(avg_duration, 1),
                escalation_rate=_rate(escalated, count),
                resolution_rate=_rate(resolved, count),
            )
        )

    return sorted(results, key=lambda r: r.count, reverse=True)


class ClientStats(BaseModel):
    client: str
    count: int
    escalation_count: int
    escalation_rate: float
    web_help_count: int
    web_help_rate: float


@router.get("/by-client", response_model=List[ClientStats])
def by_client():
    calls = load_calls()
    grouped: dict[str, list] = defaultdict(list)
    for c in calls:
        grouped[c.client].append(c)

    results = []
    for client, group in grouped.items():
        count = len(group)
        escalated = sum(1 for c in group if c.escalated_to_coordinator)
        web_help = sum(1 for c in group if c.call_reason.startswith("Web portal"))
        results.append(
            ClientStats(
                client=client,
                count=count,
                escalation_count=escalated,
                escalation_rate=_rate(escalated, count),
                web_help_count=web_help,
                web_help_rate=_rate(web_help, count),
            )
        )

    return sorted(results, key=lambda r: r.count, reverse=True)


class SentimentTrendPoint(BaseModel):
    period: str
    avg_sentiment: float
    call_count: int


class HighRiskCall(BaseModel):
    call_id: str
    client: str
    call_reason: str
    escalation_risk_flag: str
    sentiment_score: Optional[float]
    complexity_score: Optional[float]


class TranscriptInsights(BaseModel):
    total_calls: int
    scored_calls: int
    avg_sentiment: Optional[float]
    avg_complexity: Optional[float]
    sentiment_trend: List[SentimentTrendPoint]
    risk_distribution: dict
    high_risk_calls: List[HighRiskCall]


@router.get("/transcript-insights", response_model=TranscriptInsights)
def transcript_insights():
    calls = load_calls()
    scored = [c for c in calls if c.sentiment_score is not None]
    complexity_scored = [c for c in calls if c.complexity_score is not None]

    trend_groups: dict[str, list] = defaultdict(list)
    for c in scored:
        period = c.timestamp.strftime("%Y-%m")
        trend_groups[period].append(c.sentiment_score)

    sentiment_trend = [
        SentimentTrendPoint(
            period=period,
            avg_sentiment=round(sum(scores) / len(scores), 3),
            call_count=len(scores),
        )
        for period, scores in sorted(trend_groups.items())
    ]

    risk_distribution = Counter(c.escalation_risk_flag or "unscored" for c in calls)
    high_risk_calls = [
        HighRiskCall(
            call_id=c.call_id,
            client=c.client,
            call_reason=c.call_reason,
            escalation_risk_flag=c.escalation_risk_flag,
            sentiment_score=c.sentiment_score,
            complexity_score=c.complexity_score,
        )
        for c in calls
        if c.escalation_risk_flag == "high"
    ]

    return TranscriptInsights(
        total_calls=len(calls),
        scored_calls=len(scored),
        avg_sentiment=round(sum(c.sentiment_score for c in scored) / len(scored), 3) if scored else None,
        avg_complexity=round(sum(c.complexity_score for c in complexity_scored) / len(complexity_scored), 3)
        if complexity_scored
        else None,
        sentiment_trend=sentiment_trend,
        risk_distribution=dict(risk_distribution),
        high_risk_calls=high_risk_calls,
    )


class ReasonCount(BaseModel):
    call_reason: str
    count: int


class ProvinceStats(BaseModel):
    province: str
    count: int
    escalation_rate: float
    top_reasons: List[ReasonCount]


@router.get("/by-province", response_model=List[ProvinceStats])
def by_province():
    calls = load_calls()
    grouped: dict[str, list] = defaultdict(list)
    for c in calls:
        grouped[c.caller_province].append(c)

    results = []
    for province, group in grouped.items():
        count = len(group)
        escalated = sum(1 for c in group if c.escalated_to_coordinator)
        top_reasons = [
            ReasonCount(call_reason=reason, count=n)
            for reason, n in Counter(c.call_reason for c in group).most_common(3)
        ]
        results.append(
            ProvinceStats(
                province=province,
                count=count,
                escalation_rate=_rate(escalated, count),
                top_reasons=top_reasons,
            )
        )

    return sorted(results, key=lambda r: r.count, reverse=True)
