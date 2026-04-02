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

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false)

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className={`drawer-backdrop ${drawerOpen ? 'open' : ''}`} onClick={() => setDrawerOpen(false)} />
        <aside className={`drawer ${drawerOpen ? 'open' : ''}`} aria-label="功能面板">
          <div className="drawer-header">
            <h2 className="drawer-title">功能面板</h2>
            <button className="drawer-close" aria-label="关闭功能面板" onClick={() => setDrawerOpen(false)}>
              ×
            </button>
          </div>

          <section className="panel">
            <div className="panel-title">快速操作</div>
            <div className="panel-body">
              <QuickActionsPanel />
            </div>
          </section>

          <section className="panel">
            <div className="panel-title">数据看板</div>
            <div className="panel-body">
              <SummaryPanel />
            </div>
          </section>

          <section className="panel">
            <div className="panel-title">来源分布</div>
            <div className="panel-body">
              <SourceStatsPanel />
            </div>
          </section>

          <section className="panel">
            <div className="panel-title">事件脉络</div>
            <div className="panel-body">
              <EventsPanel />
            </div>
          </section>
        </aside>

        <Routes>
          <Route path="/" element={<FeedPage onOpenMenu={() => setDrawerOpen(true)} />} />
          <Route path="/items/:itemId" element={<ReaderPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
