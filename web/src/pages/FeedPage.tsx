import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getItems } from '../api/items'
import { AppHeader } from '../components/layout/AppHeader'
import { CategoryFilter } from '../components/feed/CategoryFilter'
import { FeedList } from '../components/feed/FeedList'
import { Loading } from '../components/common/Loading'
import { EmptyState } from '../components/common/EmptyState'
import { ErrorState } from '../components/common/ErrorState'

interface FeedPageProps {
  onOpenMenu: () => void
}

export function FeedPage({ onOpenMenu }: FeedPageProps) {
  const [category, setCategory] = useState('all')

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['items', category],
    queryFn: () => getItems(category),
  })

  const items = useMemo(() => data ?? [], [data])

  return (
    <main className="app-shell">
      <div className="app">
        <AppHeader onOpenMenu={onOpenMenu} />

        <section className="panel inline-panel">
          <div className="panel-body">
            <CategoryFilter value={category} onChange={setCategory} />
          </div>
        </section>

        <div className="feed-title">内容卡片</div>

        {isLoading && <Loading />}
        {isError && <ErrorState text={`加载失败：${error instanceof Error ? error.message : '未知错误'}`} />}
        {!isLoading && !isError && items.length === 0 && <EmptyState text="暂无内容" />}
        {!isLoading && !isError && items.length > 0 && <FeedList items={items} />}
      </div>
    </main>
  )
}
