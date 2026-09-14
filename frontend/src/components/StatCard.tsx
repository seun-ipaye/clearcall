interface StatCardProps {
  label: string
  value: string
  sublabel?: string
}

function StatCard({ label, value, sublabel }: StatCardProps) {
  return (
    <div
      style={{
        border: '1px solid var(--color-border)',
        background: 'var(--color-surface)',
        padding: '14px 16px',
        minWidth: 180,
      }}
    >
      <h3 style={{ margin: '0 0 6px 0' }}>{label}</h3>
      <div style={{ fontSize: 26, fontWeight: 700, lineHeight: 1.1 }}>{value}</div>
      {sublabel && (
        <div style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 4 }}>{sublabel}</div>
      )}
    </div>
  )
}

export default StatCard
