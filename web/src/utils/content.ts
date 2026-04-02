import DOMPurify from 'dompurify'
import type { Item } from '../types/item'

export function normalizeReadableText(text: string): string {
  return text
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n')
    .map((line) => line.trim())
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

export function stripHtml(text: string): string {
  if (!text || !text.includes('<')) {
    return text
  }

  const div = document.createElement('div')
  div.innerHTML = text
  return div.textContent || ''
}

export function isHtmlContent(text: string): boolean {
  return /<[a-z][\s\S]*>/i.test(text)
}

export function getPreviewContent(item: Item): string {
  const raw = item.summary || item.raw_content || ''
  const content = normalizeReadableText(stripHtml(raw))
  if (!content) {
    return '暂无正文'
  }

  const oneLine = content.replace(/\n+/g, ' ')
  return oneLine.length > 180 ? `${oneLine.slice(0, 180)}...` : oneLine
}

export function getReaderContent(item: Item): string {
  return item.raw_content || item.summary || '暂无正文'
}

export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html)
}
