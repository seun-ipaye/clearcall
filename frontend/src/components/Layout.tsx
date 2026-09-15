import { NavLink, Outlet } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', label: 'Overview', end: true },
  { to: '/by-reason', label: 'By Call Reason' },
  { to: '/by-client', label: 'By Client' },
  { to: '/by-province', label: 'By Province' },
  { to: '/transcript-insights', label: 'Transcript Insights' },
]

function Layout() {
  return (
    <div style={{ minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
      <header
        style={{
          background: 'var(--color-primary)',
          color: '#ffffff',
          padding: '10px 20px',
          borderBottom: '1px solid var(--color-primary-dark)',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
        }}
      >
        <span style={{ fontSize: 17, fontWeight: 700, letterSpacing: '0.02em' }}>ClearCall</span>
        <span className="header-subtitle" style={{ marginLeft: 10, fontSize: 12, color: '#cfe0d8' }}>
          Call Center Analytics — GreenShield &amp; Partner Clients
        </span>
      </header>

      <nav
        style={{
          display: 'flex',
          background: 'var(--color-surface)',
          borderBottom: '1px solid var(--color-border-strong)',
          padding: '0 12px',
          overflowX: 'auto',
        }}
      >
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            style={({ isActive }) => ({
              display: 'inline-block',
              padding: '10px 14px',
              fontSize: 13,
              fontWeight: isActive ? 700 : 400,
              color: isActive ? 'var(--color-primary)' : 'var(--color-text)',
              textDecoration: 'none',
              borderBottom: isActive ? '2px solid var(--color-primary)' : '2px solid transparent',
              whiteSpace: 'nowrap',
            })}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <main style={{ flex: 1, padding: 20 }}>
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
