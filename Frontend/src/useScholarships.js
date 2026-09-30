import { useEffect, useState } from 'react'

export function useScholarships() {
  const [items, setItems] = useState([])
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    const controller = new AbortController()
    fetch('/api/scholarships', { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error('failed')
        return response.json()
      })
      .then((data) => {
        setItems(data)
        setStatus('ready')
      })
      .catch(() => {
        if (!controller.signal.aborted) setStatus('error')
      })
    return () => controller.abort()
  }, [])

  return { items, status }
}
