import { Link } from 'react-router-dom'
import type { Item } from '../../types/item'
import { formatDate } from '../../utils/format'
import { getPreviewContent } from '../../utils/content'

export function FeedCard({ item }: { item: Item }) {
  return (
    <article className="item-card">
      <Link to={`/items/${item.id}`} className="card-link">
        <h3 className="item-title">{item.title}</h3>
        <div className="item-meta">
          <span>{item.source_name}</span>
          <span>{formatDate(item.published_at)}</span>
          <span className="chip">{item.category || 'general'}</span>
        </div>
        <p className="item-summary">{getPreviewContent(item)}</p>
      </Link>
      <a
        href={item.url || '#'}
        target="_blank"
        rel="noopener noreferrer"
        className="source-link"
        onClick={(e) => e.stopPropagation()}
      >
        查看原文
      </a>
    </article>
  )
}
