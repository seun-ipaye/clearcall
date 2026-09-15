export function LoadingState() {
  return <p style={{ color: 'var(--color-text-muted)' }}>Loading...</p>
}

export function ErrorState({ message }: { message: string }) {
  return <p style={{ color: 'var(--color-danger)' }}>Failed to load data: {message}</p>
}
