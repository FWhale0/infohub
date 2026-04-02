import { useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { FeedPage } from './pages/FeedPage'
import { ReaderPage } from './pages/ReaderPage'
import { QuickActionsPanel } from './components/dashboard/QuickActionsPanel'
import { SummaryPanel } from './components/dashboard/SummaryPanel'
import { SourceStatsPanel } from './components/dashboard/SourceStatsPanel'
import { EventsPanel } from './components/dashboard/EventsPanel'
import './index.css'

const queryClient = new QueryClient()

// Sidebar content component for desktop
function SidebarContent() {
  return (
    <>
      <div className="sidebar-section">
        <div className="sidebar-title">快速操作</div>
        <QuickActionsPanel />
      </div>

      <div className="sidebar-section">
        <div className="sidebar-title">数据概览</div>
        <SummaryPanel />
      </div>

      <div className="sidebar-section">
        <div className="sidebar-title">来源分布</div>
        <SourceStatsPanel />
      </div>

      <div className="sidebar-section">
        <div className="sidebar-title">事件脉络</div>
        <EventsPanel />
      </div>
    </>
  )
}

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false)

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {/* Mobile Drawer Backdrop */}
        <div
          className={`drawer-backdrop ${drawerOpen ? 'open' : ''}`}
          onClick={() => setDrawerOpen(false)}
        />

        {/* Mobile Drawer */}
        <aside className={`drawer ${drawerOpen ? 'open' : ''}`} aria-label="功能面板">
          <div className="drawer-header">
            <h2 className="drawer-title">功能面板</h2>
            <button
              className="drawer-close"
              aria-label="关闭功能面板"
              onClick={() => setDrawerOpen(false)}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <SidebarContent />
        </aside>

        {/* Desktop Sidebar */}
        <aside className="sidebar" aria-label="功能面板">
          <div className="sidebar-header">
            <div className="logo" style={{ fontSize: '20px', marginBottom: '8px' }}>InfoHub</div>
            <p className="tagline" style={{ fontSize: '13px' }}>AI 驱动的信息聚合</p>
          </div>
          <SidebarContent />
        </aside>

        <Routes>
          <Route
            path="/"
            element={<FeedPage onOpenMenu={() => setDrawerOpen(true)} />}
          />
          <Route path="/items/:itemId" element={<ReaderPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
