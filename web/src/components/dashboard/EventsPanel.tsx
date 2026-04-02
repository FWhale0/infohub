import { useQuery } from '@tanstack/react-query'
import { getEvents } from '../../api/dashboard'
import { Loading } from '../common/Loading'
import { ErrorState } from '../common/ErrorState'
import { EmptyState } from '../common/EmptyState'

export function EventsPanel() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['dashboard', 'events'],
    queryFn: getEvents,
  })

  if (isLoading) return <Loading text="加载事件中..." />
  if (isError) return <ErrorState text={`加载失败：${error instanceof Error ? error.message : '未知错误'}`} />
  if (!data || data.length === 0) return <EmptyState text="暂无事件，执行处理后会逐步生成" />

  return (
    <div>
      {data.map((event) => (
        <div key={event.topic} className="event-item">
          <span>{event.topic || '未命名事件'}</span>
          <strong>{event.item_count || 0}</strong>
        </div>
      ))}
    </div>
  )
}
