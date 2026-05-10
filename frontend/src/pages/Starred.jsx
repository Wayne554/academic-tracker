import React, { useState, useEffect } from 'react'
import { useStore, api } from '../store'
import PaperCard from '../components/PaperCard'
import Header from '../components/Header'

export default function Starred() {
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await api.get('/papers', { params: { starred_only: true } })
      setPapers(res.data.papers)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleStar = async (paperId) => {
    await api.post(`/papers/${paperId}/star`)
    fetchData()
  }

  const handleMarkRead = async (paperId) => {
    await api.post(`/papers/${paperId}/read`)
    fetchData()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="p-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">我的星标</h1>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="bg-white p-4 rounded-lg shadow animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {papers.map(paper => (
                <PaperCard
                  key={paper.id}
                  paper={paper}
                  onStar={handleStar}
                  onMarkRead={handleMarkRead}
                />
              ))}
              {papers.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                  暂无星标论文
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
