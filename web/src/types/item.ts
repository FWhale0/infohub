export interface Item {
  id: number
  title: string
  url: string
  source_type: string
  source_name: string
  summary: string | null
  raw_content: string | null
  quality_score: number
  category: string
  published_at: string
  created_at: string
}
