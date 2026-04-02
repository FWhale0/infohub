interface AppHeaderProps {
  onOpenMenu: () => void
}

export function AppHeader({ onOpenMenu }: AppHeaderProps) {
  return (
    <header className="app-header">
      <div className="header-main">
        <div className="logo">InfoHub</div>
        <p className="tagline">AI 驱动的信息聚合</p>
      </div>
      <button className="menu-btn" aria-label="打开功能面板" onClick={onOpenMenu}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
    </header>
  )
}
