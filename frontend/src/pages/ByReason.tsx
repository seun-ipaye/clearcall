import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Tooltip,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from 'recharts'
import { getReasonStats } from '../api/client'
import Panel from '../components/Panel'
import { useApi } from '../hooks/useApi'
import { COLORS, tooltipStyle } from '../theme'
import { formatDuration, formatPercent } from '../utils/format'
import type { ReasonStats } from '../api/types'
import { ErrorState, LoadingState } from '../components/Status'

const TOP_N = 10

function topBy(data: ReasonStats[], key: keyof ReasonStats, n: number) {
  return [...data].sort((a, b) => (b[key] as number) - (a[key] as number)).slice(0, n)
}

function riskColor(rate: number) {
  if (rate >= 0.2) return COLORS.danger
  if (rate >= 0.1) return COLORS.accent
  return COLORS.primary
}

function ByReason() {
  const { data, loading, error } = useApi(getReasonStats, [])

  return (
    <div>
      <h2>By Call Reason</h2>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}

      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <Panel title={`Call Volume — Top ${TOP_N} Reasons`}>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart
                data={topBy(data, 'count', TOP_N)}
                layout="vertical"
                margin={{ top: 4, right: 16, bottom: 4, left: 4 }}
              >
                <CartesianGrid stroke={COLORS.border} horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                <YAxis
                  type="category"
                  dataKey="call_reason"
                  width={220}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="count" name="Calls" fill={COLORS.primary} />
              </BarChart>
            </ResponsiveContainer>
          </Panel>

          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <div style={{ flex: '1 1 360px' }}>
              <Panel title="Longest Average Handle Time">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart
                    data={topBy(data, 'avg_duration_seconds', 8)}
                    layout="vertical"
                    margin={{ top: 4, right: 16, bottom: 4, left: 4 }}
                  >
                    <CartesianGrid stroke={COLORS.border} horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v) => `${Math.round(v / 60)}m`} />
                    <YAxis type="category" dataKey="call_reason" width={200} tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={tooltipStyle}
                      formatter={(value) => formatDuration(Number(value))}
                    />
                    <Bar dataKey="avg_duration_seconds" name="Avg duration" fill={COLORS.accent} />
                  </BarChart>
                </ResponsiveContainer>
              </Panel>
            </div>

            <div style={{ flex: '1 1 360px' }}>
              <Panel title="Highest Escalation Rate">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart
                    data={topBy(data, 'escalation_rate', 8)}
                    layout="vertical"
                    margin={{ top: 4, right: 16, bottom: 4, left: 4 }}
                  >
                    <CartesianGrid stroke={COLORS.border} horizontal={false} />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 11 }}
                      tickFormatter={(v) => formatPercent(v, 0)}
                    />
                    <YAxis type="category" dataKey="call_reason" width={200} tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={tooltipStyle} formatter={(value) => formatPercent(Number(value))} />
                    <Bar dataKey="escalation_rate" name="Escalation rate">
                      {topBy(data, 'escalation_rate', 8).map((row) => (
                        <Cell key={row.call_reason} fill={riskColor(row.escalation_rate)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Panel>
            </div>
          </div>

          <Panel title="All Call Reasons">
            <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Call Reason</th>
                  <th>Count</th>
                  <th>Avg Handle Time</th>
                  <th>Escalation Rate</th>
                  <th>Resolution Rate</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr key={row.call_reason}>
                    <td>{row.call_reason}</td>
                    <td>{row.count}</td>
                    <td>{formatDuration(row.avg_duration_seconds)}</td>
                    <td>{formatPercent(row.escalation_rate)}</td>
                    <td>{formatPercent(row.resolution_rate)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </Panel>
        </div>
      )}
    </div>
  )
}

export default ByReason
