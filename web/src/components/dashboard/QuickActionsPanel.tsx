import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { runFetchNow, runProcessNow } from '../../api/dashboard'

export function QuickActionsPanel() {
  const queryClient = useQueryClient()
  const [status, setStatus] = useState('')
  const [running, setRunning] = useState<'fetch' | 'process' | null>(null)

  async function handleRun(type: 'fetch' | 'process') {
    setRunning(type)
    setStatus(type === 'fetch' ? '正在采集，请稍候...' : '正在处理，请稍候...')

    try {
      const data = type === 'fetch' ? await runFetchNow() : await runProcessNow()
      setStatus(data.message || '操作完成')
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['items'] }),
        queryClient.invalidateQueries({ queryKey: ['dashboard'] }),
        queryClient.invalidateQueries({ queryKey: ['sources'] }),
      ])
    } catch (error) {
      setStatus(`操作失败：${error instanceof Error ? error.message : '未知错误'}`)
    } finally {
      setRunning(null)
    }
  }

  return (
    <>
      <div className="button-group">
        <button className="btn fetch" onClick={() => handleRun('fetch')} disabled={running !== null}>
          {running === 'fetch' ? '采集中...' : '立即采集'}
        </button>
        <button className="btn process" onClick={() => handleRun('process')} disabled={running !== null}>
          {running === 'process' ? '处理中...' : '立即处理'}
        </button>
      </div>
      <div className="status">{status}</div>
    </>
  )
}
