import { apiFetch } from './client'
import type { DailySummary, EventGroup } from '../types/dashboard'

export async function getSummary(): Promise<DailySummary> {
  return apiFetch<DailySummary>('/dashboard/summary')
}

export async function getEvents(): Promise<EventGroup[]> {
  return apiFetch<EventGroup[]>('/dashboard/events')
}

export async function runFetchNow(): Promise<{ status: string; message: string }> {
  return apiFetch('/dashboard/run-fetch', { method: 'POST' })
}

export async function runProcessNow(): Promise<{ status: string; message: string }> {
  return apiFetch('/dashboard/run-process', { method: 'POST' })
}
