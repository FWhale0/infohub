export function formatDate(dateStr: string): string {
  if (!dateStr) {
    return ''
  }

  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
