import { apiFetch } from './client'
import type { Source } from '../types/source'

export async function getSources(): Promise<Source[]> {
  return apiFetch<Source[]>('/sources/')
}
