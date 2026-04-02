export interface Source {
  id: number
  type: 'rss' | 'news' | 'newsletter'
  name: string
  url: string
  category: string
  is_active: boolean
  created_at: string
  last_fetch: string | null
}
