import type { Item } from '../../types/item'
import { formatDate } from '../../utils/format'
import { getReaderContent, isHtmlContent, normalizeReadableText, sanitizeHtml } from '../../utils/content'

export function ReaderContent({ item }: { item: Item }) {
  const raw = getReaderContent(item)
  const html = isHtmlContent(raw)

  if (html) {
    return (
      <div
        className="reader-content rich"
        dangerouslySetInnerHTML={{ __html: sanitizeHtml(raw) }}
      />
    )
  }

  return <div className="reader-content plain">{normalizeReadableText(raw)}</div>
}

export function ReaderMeta({ item }: { item: Item }) {
  return (
    <div className="reader-meta">
      <span>{item.source_name}</span>
      <span>{formatDate(item.published_at)}</span>
      <span className="chip">{item.category || 'general'}</span>
    </div>
  )
}
