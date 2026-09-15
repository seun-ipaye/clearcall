import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis, ResponsiveContainer } from 'recharts'
import { getProvinceStats } from '../api/client'
import Panel from '../components/Panel'
import { useApi } from '../hooks/useApi'
import { COLORS, tooltipStyle } from '../theme'
import { formatPercent } from '../utils/format'

function ByProvince() {
  const { data, loading, error } = useApi(getProvinceStats, [])

  return (
    <div>
      <h2>By Province</h2>

      {loading && <p style={{ color: 'var(--color-text-muted)' }}>Loading...</p>}
      {error && <p style={{ color: 'var(--color-danger)' }}>Failed to load province stats: {error}</p>}

      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <Panel title="Call Volume by Province">
            <ResponsiveContainer width="100%" height={360}>
              <BarChart
                data={data}
                layout="vertical"
                margin={{ top: 4, right: 16, bottom: 4, left: 4 }}
              >
                <CartesianGrid stroke={COLORS.border} horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                <YAxis type="category" dataKey="province" width={40} tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="count" name="Calls" fill={COLORS.primary} />
              </BarChart>
            </ResponsiveContainer>
          </Panel>

          <Panel title="Province Detail">
            <table>
              <thead>
                <tr>
                  <th>Province</th>
                  <th>Calls</th>
                  <th>Escalation Rate</th>
                  <th>Top Call Reasons</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr key={row.province}>
                    <td>{row.province}</td>
                    <td>{row.count}</td>
                    <td>{formatPercent(row.escalation_rate)}</td>
                    <td>
                      {row.top_reasons.map((r) => `${r.call_reason} (${r.count})`).join(' · ')}
                    </td>
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

export default ByProvince
