export type CallerType = 'plan_member' | 'provider'
export type ResolutionStatus = 'resolved' | 'unresolved' | 'transferred'
export type ClientName = 'GreenShield' | 'RBC Insurance' | 'Wawanesa' | 'Victor Insurance' | 'Entente'
export type EscalationRisk = 'low' | 'medium' | 'high'

export interface TranscriptTurn {
  speaker: 'Agent' | 'Caller'
  text: string
}

export interface CallRecord {
  call_id: string
  timestamp: string
  duration_seconds: number
  caller_type: CallerType
  client: ClientName
  call_reason: string
  escalated_to_coordinator: boolean
  escalation_notes: string | null
  agent_id: string
  caller_province: string
  resolution_status: ResolutionStatus
  transcript: TranscriptTurn[]
  sentiment_score: number | null
  complexity_score: number | null
  escalation_risk_flag: EscalationRisk | null
}

export interface CallListFilters {
  client?: ClientName
  caller_type?: CallerType
  call_reason?: string
  escalated_to_coordinator?: boolean
  resolution_status?: ResolutionStatus
  caller_province?: string
  limit?: number
  offset?: number
}

export interface OverviewStats {
  total_calls: number
  avg_handle_time_seconds: number
  escalation_rate: number
  resolution_rate: number
}

export interface ReasonStats {
  call_reason: string
  count: number
  avg_duration_seconds: number
  escalation_rate: number
  resolution_rate: number
}

export interface ClientStats {
  client: ClientName
  count: number
  escalation_count: number
  escalation_rate: number
  web_help_count: number
  web_help_rate: number
}

export interface ReasonCount {
  call_reason: string
  count: number
}

export interface ProvinceStats {
  province: string
  count: number
  escalation_rate: number
  top_reasons: ReasonCount[]
}

export interface SentimentTrendPoint {
  period: string
  avg_sentiment: number
  call_count: number
}

export interface HighRiskCall {
  call_id: string
  client: ClientName
  call_reason: string
  escalation_risk_flag: EscalationRisk
  sentiment_score: number | null
  complexity_score: number | null
}

export interface TranscriptInsights {
  total_calls: number
  scored_calls: number
  avg_sentiment: number | null
  avg_complexity: number | null
  sentiment_trend: SentimentTrendPoint[]
  risk_distribution: Record<string, number>
  high_risk_calls: HighRiskCall[]
}
