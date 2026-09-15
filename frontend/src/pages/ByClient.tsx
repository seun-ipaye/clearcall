import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis, ResponsiveContainer } from 'recharts'
import { getClientStats } from '../api/client'
import Panel from '../components/Panel'
import { useApi } from '../hooks/useApi'
import { COLORS, tooltipStyle } from '../theme'
import { formatPercent } from '../utils/format'

function ByClient() {
  const { data, loading, error } = useApi(getClientStats, [])

  return (
    <div>
      <h2>By Client</h2>

      {loading && <p style={{ color: 'var(--color-text-muted)' }}>Loading...</p>}
      {error && <p style={{ color: 'var(--color-danger)' }}>Failed to load client stats: {error}</p>}

      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <div style={{ flex: '1 1 280px' }}>
              <Panel title="Call Volume">
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
                    <CartesianGrid stroke={COLORS.border} vertical={false} />
                    <XAxis dataKey="client" tick={{ fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={50} />
                    <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Bar dataKey="count" name="Calls" fill={COLORS.primary} />
                  </BarChart>
                </ResponsiveContainer>
              </Panel>
            </div>

            <div style={{ flex: '1 1 280px' }}>
              <Panel title="Web Help Rate">
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
                    <CartesianGrid stroke={COLORS.border} vertical={false} />
                    <XAxis dataKey="client" tick={{ fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={50} />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatPercent(v, 0)} />
                    <Tooltip contentStyle={tooltipStyle} formatter={(value: number) => formatPercent(value)} />
                    <Bar dataKey="web_help_rate" name="Web help rate" fill={COLORS.accent} />
                  </BarChart>
                </ResponsiveContainer>
              </Panel>
            </div>

            <div style={{ flex: '1 1 280px' }}>
              <Panel title="Escalation Rate">
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={data} margin={{ top: 4, right: 8, bottom: 4, left: 0 }}>
                    <CartesianGrid stroke={COLORS.border} vertical={false} />
                    <XAxis dataKey="client" tick={{ fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={50} />
                    <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatPercent(v, 0)} />
                    <Tooltip contentStyle={tooltipStyle} formatter={(value: number) => formatPercent(value)} />
                    <Bar dataKey="escalation_rate" name="Escalation rate" fill={COLORS.danger} />
                  </BarChart>
                </ResponsiveContainer>
              </Panel>
            </div>
          </div>

          <Panel title="Client Summary">
            <table>
              <thead>
                <tr>
                  <th>Client</th>
                  <th>Calls</th>
                  <th>Web Help Calls</th>
                  <th>Web Help Rate</th>
                  <th>Escalations</th>
                  <th>Escalation Rate</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr key={row.client}>
                    <td>{row.client}</td>
                    <td>{row.count}</td>
                    <td>{row.web_help_count}</td>
                    <td>{formatPercent(row.web_help_rate)}</td>
                    <td>{row.escalation_count}</td>
                    <td>{formatPercent(row.escalation_rate)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        </div>
      )}
    </div>
  )
}

export default ByClient
