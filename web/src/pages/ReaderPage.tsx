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
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '6px' }}>
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          返回
        </Link>
        <a
          className="reader-btn primary"
          href={item.url || '#'}
          target="_blank"
          rel="noopener noreferrer"
        >
          查看原文
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: '4px' }}>
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
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
