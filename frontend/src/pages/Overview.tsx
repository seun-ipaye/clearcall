import { getOverviewStats } from '../api/client'
import StatCard from '../components/StatCard'
import { useApi } from '../hooks/useApi'
import { formatDuration, formatPercent } from '../utils/format'

function Overview() {
  const { data, loading, error } = useApi(getOverviewStats, [])

  return (
    <div>
      <h2>Overview</h2>

      {loading && <p style={{ color: 'var(--color-text-muted)' }}>Loading...</p>}
      {error && <p style={{ color: 'var(--color-danger)' }}>Failed to load overview stats: {error}</p>}

      {data && (
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <StatCard label="Total Calls" value={data.total_calls.toLocaleString()} />
          <StatCard
            label="Avg Handle Time"
            value={formatDuration(data.avg_handle_time_seconds)}
            sublabel={`${data.avg_handle_time_seconds}s`}
          />
          <StatCard label="Escalation Rate" value={formatPercent(data.escalation_rate)} />
          <StatCard label="Resolution Rate" value={formatPercent(data.resolution_rate)} />
        </div>
      )}
    </div>
  )
}

export default Overview
