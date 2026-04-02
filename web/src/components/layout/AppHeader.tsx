interface AppHeaderProps {
  onOpenMenu: () => void
}

export function AppHeader({ onOpenMenu }: AppHeaderProps) {
  return (
    <header className="app-header">
      <div className="header-main">
        <div className="logo">InfoHub</div>
        <p className="tagline">AI 驱动的信息聚合与筛选</p>
      </div>
      <button className="menu-btn" aria-label="打开功能面板" onClick={onOpenMenu}>
        ≡
      </button>
    </header>
  )
}
