import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getItem } from '../api/items'
import { Loading } from '../components/common/Loading'
import { ErrorState } from '../components/common/ErrorState'
import { ReaderContent, ReaderMeta } from '../components/reader/ReaderContent'

export function ReaderPage() {
  const { itemId = '' } = useParams()

  const { data: item, isLoading, isError, error } = useQuery({
    queryKey: ['item', itemId],
    queryFn: () => getItem(itemId),
    enabled: Boolean(itemId),
  })

  if (isLoading) {
    return <Loading text="正在加载正文..." />
  }

  if (isError || !item) {
    return <ErrorState text={`加载失败：${error instanceof Error ? error.message : '未找到文章'}`} />
  }

  return (
    <div className="reader-page">
      <div className="reader-topbar">
        <Link className="reader-btn" to="/">
          ← 返回
        </Link>
        <a
          className="reader-btn primary"
          href={item.url || '#'}
          target="_blank"
          rel="noopener noreferrer"
        >
          查看原文 ↗
        </a>
      </div>
      <div className="reader-body">
        <h1 className="reader-title">{item.title}</h1>
        <ReaderMeta item={item} />
        <ReaderContent item={item} />
      </div>
    </div>
  )
}
