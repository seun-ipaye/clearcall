import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis,
  ResponsiveContainer,
} from 'recharts'
import { getTranscriptInsights } from '../api/client'
import Panel from '../components/Panel'
import StatCard from '../components/StatCard'
import { useApi } from '../hooks/useApi'
import { COLORS, tooltipStyle } from '../theme'
import { ErrorState, LoadingState } from '../components/Status'

const RISK_ORDER = ['low', 'medium', 'high', 'unscored']
const RISK_COLORS: Record<string, string> = {
  low: COLORS.primary,
  medium: COLORS.accent,
  high: COLORS.danger,
  unscored: COLORS.borderStrong,
}

function TranscriptInsights() {
  const { data, loading, error } = useApi(getTranscriptInsights, [])

  return (
    <div>
      <h2>Transcript Insights</h2>

      {loading && <LoadingState />}
      {error && <ErrorState message={error} />}

      {data && data.scored_calls === 0 && (
        <Panel title="Analysis Pending">
          <p>
            None of the {data.total_calls} calls have been run through the transcript analysis
            pipeline yet. Sentiment trends, complexity scores, and escalation-risk flags will appear
            here once the Claude-powered pipeline runs (requires an{' '}
            <code>ANTHROPIC_API_KEY</code>).
          </p>
        </Panel>
      )}

      {data && data.scored_calls > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <StatCard label="Calls Analyzed" value={`${data.scored_calls} / ${data.total_calls}`} />
            <StatCard
              label="Avg Sentiment"
              value={data.avg_sentiment !== null ? data.avg_sentiment.toFixed(2) : '—'}
              sublabel="-1 (negative) to 1 (positive)"
            />
            <StatCard
              label="Avg Complexity"
              value={data.avg_complexity !== null ? data.avg_complexity.toFixed(1) : '—'}
              sublabel="0 (trivial) to 10 (complex)"
            />
            <StatCard
              label="High Risk Calls"
              value={String(data.risk_distribution.high ?? 0)}
            />
          </div>

          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <div style={{ flex: '2 1 420px' }}>
              <Panel title="Sentiment Trend">
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={data.sentiment_trend} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                    <CartesianGrid stroke={COLORS.border} vertical={false} />
                    <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                    <YAxis domain={[-1, 1]} tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Line
                      type="monotone"
                      dataKey="avg_sentiment"
                      name="Avg sentiment"
                      stroke={COLORS.primary}
                      strokeWidth={2}
                      dot={{ r: 3 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Panel>
            </div>

            <div style={{ flex: '1 1 260px' }}>
              <Panel title="Escalation Risk Distribution">
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart
                    data={RISK_ORDER.filter((r) => r in data.risk_distribution).map((r) => ({
                      risk: r,
                      count: data.risk_distribution[r],
                    }))}
                    margin={{ top: 4, right: 8, bottom: 4, left: 0 }}
                  >
                    <CartesianGrid stroke={COLORS.border} vertical={false} />
                    <XAxis dataKey="risk" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Bar dataKey="count" name="Calls">
                      {RISK_ORDER.filter((r) => r in data.risk_distribution).map((r) => (
                        <Cell key={r} fill={RISK_COLORS[r]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Panel>
            </div>
          </div>

          <Panel title="High Risk Calls">
            {data.high_risk_calls.length === 0 ? (
              <p style={{ color: 'var(--color-text-muted)' }}>No calls currently flagged as high risk.</p>
            ) : (
              <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Call ID</th>
                    <th>Client</th>
                    <th>Call Reason</th>
                    <th>Sentiment</th>
                    <th>Complexity</th>
                  </tr>
                </thead>
                <tbody>
                  {data.high_risk_calls.map((call) => (
                    <tr key={call.call_id}>
                      <td>{call.call_id}</td>
                      <td>{call.client}</td>
                      <td>{call.call_reason}</td>
                      <td>{call.sentiment_score?.toFixed(2) ?? '—'}</td>
                      <td>{call.complexity_score?.toFixed(1) ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              </div>
            )}
          </Panel>
        </div>
      )}
    </div>
  )
}

export default TranscriptInsights
