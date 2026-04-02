import { apiFetch } from './client'
import type { Item } from '../types/item'

export async function getItems(category?: string): Promise<Item[]> {
  const query = new URLSearchParams()
  if (category && category !== 'all') {
    query.set('category', category)
  }

  const suffix = query.toString() ? `/?${query.toString()}` : '/'
  return apiFetch<Item[]>(`/items${suffix}`)
}

export async function getItem(itemId: string): Promise<Item> {
  return apiFetch<Item>(`/items/${itemId}`)
}
