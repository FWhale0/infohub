export interface CategoryStat {
  category: string
  count: number
}

export interface DailySummary {
  date: string
  total_items: number
  pending_items: number
  quality_items: number
  top_categories: CategoryStat[]
  source_distribution: Record<string, number>
}

export interface EventItem {
  id: number
  title: string
  category: string
  quality_score: number
  published_at: string
}

export interface EventGroup {
  topic: string
  item_count: number
  items: EventItem[]
  updated_at: string
}
