import { useQuery } from '@tanstack/react-query'
import { getSummary } from '../../api/dashboard'
import { Loading } from '../common/Loading'
import { ErrorState } from '../common/ErrorState'

export function SummaryPanel() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: getSummary,
  })

  if (isLoading) return <Loading text="加载看板中..." />
  if (isError || !data) {
    return <ErrorState text={`加载失败：${error instanceof Error ? error.message : '未知错误'}`} />
  }

  return (
    <div className="stats">
      <div className="stat"><h4>今日收录</h4><div className="num">{data.total_items || 0}</div></div>
      <div className="stat"><h4>待处理</h4><div className="num">{data.pending_items || 0}</div></div>
      <div className="stat"><h4>高质量内容</h4><div className="num">{data.quality_items || 0}</div></div>
      <div className="stat"><h4>活跃主题</h4><div className="num">{data.top_categories?.length || 0}</div></div>
    </div>
  )
}
