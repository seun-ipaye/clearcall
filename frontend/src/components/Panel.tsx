import type { ReactNode } from 'react'

interface PanelProps {
  title: string
  children: ReactNode
}

function Panel({ title, children }: PanelProps) {
  return (
    <div
      style={{
        border: '1px solid var(--color-border)',
        background: 'var(--color-surface)',
        padding: '14px 16px',
      }}
    >
      <h3 style={{ marginBottom: 10 }}>{title}</h3>
      {children}
    </div>
  )
}

export default Panel
