import { useQuery } from '@tanstack/react-query'
import { getSources } from '../../api/sources'
import { Loading } from '../common/Loading'
import { ErrorState } from '../common/ErrorState'
import { EmptyState } from '../common/EmptyState'

export function SourceStatsPanel() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['sources'],
    queryFn: getSources,
  })

  if (isLoading) return <Loading text="加载来源中..." />
  if (isError) return <ErrorState text={`加载失败：${error instanceof Error ? error.message : '未知错误'}`} />

  const byType = (data ?? []).reduce<Record<string, number>>((acc, source) => {
    const type = (source.type || 'unknown').toUpperCase()
    acc[type] = (acc[type] || 0) + 1
    return acc
  }, {})

  const entries = Object.entries(byType)
  if (entries.length === 0) return <EmptyState text="暂无来源" />

  return (
    <div>
      {entries.map(([type, count]) => (
        <div key={type} className="source-item">
          <span>{type}</span>
          <strong>{count}</strong>
        </div>
      ))}
    </div>
  )
}
