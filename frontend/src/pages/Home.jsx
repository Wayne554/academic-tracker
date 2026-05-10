import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useStore, api } from '../store'
import PaperCard from '../components/PaperCard'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'

export default function Home() {
  const [papers, setPapers] = useState([])
  const [journals, setJournals] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    journal_id: null,
    category_id: null,
    search: '',
    sort: 'date',
    unread_only: false
  })
  const [total, setTotal] = useState(0)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [papersRes, journalsRes, categoriesRes] = await Promise.all([
        api.get('/papers', { params: filters }),
        api.get('/journals'),
        api.get('/categories')
      ])
      setPapers(papersRes.data.papers)
      setTotal(papersRes.data.total)
      setJournals(journalsRes.data)
      setCategories(categoriesRes.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [filters])

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
      <div className="flex">
        <Sidebar
          journals={journals}
          categories={categories}
          filters={filters}
          setFilters={setFilters}
        />
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h1 className="text-2xl font-bold text-gray-900">论文列表</h1>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilters(f => ({ ...f, unread_only: !f.unread_only }))}
                  className={`px-3 py-1 rounded text-sm ${filters.unread_only ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  仅未读
                </button>
                <select
                  value={filters.sort}
                  onChange={(e) => setFilters(f => ({ ...f, sort: e.target.value }))}
                  className="px-3 py-1 border rounded text-sm"
                >
                  <option value="date">按日期</option>
                  <option value="journal">按期刊</option>
                  <option value="title">按标题</option>
                </select>
              </div>
            </div>
            <div className="relative">
              <input
                type="text"
                placeholder="搜索论文..."
                value={filters.search}
                onChange={(e) => setFilters(f => ({ ...f, search: e.target.value }))}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map(i => (
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
                    暂无论文
                  </div>
                )}
              </div>
            )}
            <div className="text-center text-sm text-gray-500">
              共 {total} 篇论文
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
