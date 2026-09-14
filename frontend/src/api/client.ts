import type {
  CallListFilters,
  CallRecord,
  ClientStats,
  OverviewStats,
  ProvinceStats,
  ReasonStats,
  TranscriptInsights,
} from './types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new ApiError(res.status, body || `Request to ${path} failed with ${res.status}`)
  }
  return res.json() as Promise<T>
}

function buildQuery(filters: CallListFilters = {}): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null) {
      params.set(key, String(value))
    }
  }
  const query = params.toString()
  return query ? `?${query}` : ''
}

export function getCalls(filters?: CallListFilters): Promise<CallRecord[]> {
  return getJson(`/api/calls${buildQuery(filters)}`)
}

export function getCall(callId: string): Promise<CallRecord> {
  return getJson(`/api/calls/${encodeURIComponent(callId)}`)
}

export function getOverviewStats(): Promise<OverviewStats> {
  return getJson('/api/stats/overview')
}

export function getReasonStats(): Promise<ReasonStats[]> {
  return getJson('/api/stats/by-reason')
}

export function getClientStats(): Promise<ClientStats[]> {
  return getJson('/api/stats/by-client')
}

export function getProvinceStats(): Promise<ProvinceStats[]> {
  return getJson('/api/stats/by-province')
}

export function getTranscriptInsights(): Promise<TranscriptInsights> {
  return getJson('/api/stats/transcript-insights')
}
