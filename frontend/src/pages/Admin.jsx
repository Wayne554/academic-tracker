import React, { useState, useEffect } from 'react'
import { api } from '../store'
import Header from '../components/Header'

export default function Admin() {
  const [activeTab, setActiveTab] = useState('journals')
  const [journals, setJournals] = useState([])
  const [categories, setCategories] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [newCategory, setNewCategory] = useState('')
  const [newUser, setNewUser] = useState({ email: '', password: '' })

  const fetchData = async () => {
    setLoading(true)
    try {
      const [journalsRes, categoriesRes, usersRes] = await Promise.all([
        api.get('/journals'),
        api.get('/categories'),
        api.get('/users')
      ])
      setJournals(journalsRes.data)
      setCategories(categoriesRes.data)
      setUsers(usersRes.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleSearchJournals = async () => {
    if (!searchQuery) return
    const res = await api.get('/openalex/search', { params: { query: searchQuery } })
    setSearchResults(res.data.results)
  }

  const handleAddJournal = async (journal, selectedCategoryIds) => {
    try {
      // 确保我们发送正确的字段
      const journalData = {
        openalex_source_id: journal.id,
        issn: journal.issn,
        display_name: journal.display_name,
        publisher: journal.publisher,
        category_ids: selectedCategoryIds
      }
      
      console.log('添加期刊:', journalData)
      
      await api.post('/journals', journalData)
      setSearchResults([])
      setSearchQuery('')
      fetchData()
      alert('期刊添加成功！')
    } catch (error) {
      console.error('添加期刊失败:', error)
      alert(`添加期刊失败: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleDeleteJournal = async (id) => {
    if (window.confirm('确定删除此期刊？')) {
      await api.delete(`/journals/${id}`)
      fetchData()
    }
  }

  const handleRefreshJournal = async (id) => {
    const res = await api.post(`/journals/${id}/refresh`)
    alert(`新增 ${res.data.new_papers} 篇论文`)
    fetchData()
  }

  const handleRefreshAll = async () => {
    const res = await api.post('/admin/refresh')
    alert(`共新增 ${res.data.new_papers} 篇论文`)
  }

  const handleAddCategory = async () => {
    if (!newCategory) return
    await api.post('/categories', { name: newCategory })
    setNewCategory('')
    fetchData()
  }

  const handleDeleteCategory = async (id) => {
    if (window.confirm('确定删除此分类？')) {
      await api.delete(`/categories/${id}`)
      fetchData()
    }
  }

  const handleAddUser = async (e) => {
    e.preventDefault()
    await api.post('/users', newUser)
    setNewUser({ email: '', password: '' })
    fetchData()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">管理后台</h1>
            <button
              onClick={handleRefreshAll}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              刷新所有期刊论文
            </button>
          </div>

          <div className="border-b border-gray-200 mb-6">
            <nav className="flex space-x-8">
              {['journals', 'categories', 'users'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab === 'journals' && '期刊管理'}
                  {tab === 'categories' && '分类管理'}
                  {tab === 'users' && '用户管理'}
                </button>
              ))}
            </nav>
          </div>

          {activeTab === 'journals' && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-semibold mb-4">添加期刊</h2>
                <div className="flex gap-2 mb-4">
                  <input
                    type="text"
                    placeholder="搜索期刊名或 ISSN..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearchJournals()}
                    className="flex-1 px-4 py-2 border rounded-lg"
                  />
                  <button
                    onClick={handleSearchJournals}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    搜索
                  </button>
                </div>
                {searchResults.length > 0 && (
                  <div className="space-y-2">
                    {searchResults.map(journal => (
                      <JournalSearchResult
                        key={journal.id}
                        journal={journal}
                        categories={categories}
                        onAdd={handleAddJournal}
                      />
                    ))}
                  </div>
                )}
              </div>

              <div className="bg-white rounded-lg shadow overflow-hidden">
                <h2 className="text-lg font-semibold p-4 border-b">已添加期刊</h2>
                {loading ? (
                  <div className="p-4 text-center">加载中...</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">期刊名</th>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">ISSN</th>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">分类</th>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">操作</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {journals.map(journal => (
                        <tr key={journal.id}>
                          <td className="px-4 py-3">{journal.display_name}</td>
                          <td className="px-4 py-3">{journal.issn}</td>
                          <td className="px-4 py-3">
                            {journal.categories?.map(c => c.name).join(', ')}
                          </td>
                          <td className="px-4 py-3 space-x-2">
                            <button
                              onClick={() => handleRefreshJournal(journal.id)}
                              className="text-green-600 hover:text-green-800 text-sm"
                            >
                              刷新
                            </button>
                            <button
                              onClick={() => handleDeleteJournal(journal.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              删除
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {activeTab === 'categories' && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">分类管理</h2>
              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  placeholder="新分类名称"
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="flex-1 px-4 py-2 border rounded-lg"
                />
                <button
                  onClick={handleAddCategory}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  添加
                </button>
              </div>
              <div className="space-y-2">
                {categories.map(category => (
                  <div key={category.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span>{category.name}</span>
                    <button
                      onClick={() => handleDeleteCategory(category.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      删除
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'users' && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-semibold mb-4">添加用户</h2>
                <form onSubmit={handleAddUser} className="flex gap-2">
                  <input
                    type="email"
                    placeholder="邮箱"
                    value={newUser.email}
                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    className="flex-1 px-4 py-2 border rounded-lg"
                  />
                  <input
                    type="password"
                    placeholder="密码"
                    value={newUser.password}
                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    className="px-4 py-2 border rounded-lg w-40"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    添加
                  </button>
                </form>
              </div>
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <h2 className="text-lg font-semibold p-4 border-b">用户列表</h2>
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">邮箱</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">管理员</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">创建时间</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {users.map(user => (
                      <tr key={user.id}>
                        <td className="px-4 py-3">{user.email}</td>
                        <td className="px-4 py-3">{user.is_admin ? '是' : '否'}</td>
                        <td className="px-4 py-3">{new Date(user.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

function JournalSearchResult({ journal, categories, onAdd }) {
  const [selectedCategories, setSelectedCategories] = useState([])
  const [showCategories, setShowCategories] = useState(false)

  return (
    <div className="border p-4 rounded-lg flex items-center justify-between">
      <div>
        <div className="font-medium">{journal.display_name}</div>
        <div className="text-sm text-gray-500">{journal.publisher || ''} {journal.issn ? `| ${journal.issn}` : ''}</div>
        {showCategories && (
          <div className="mt-2 flex flex-wrap gap-2">
            {categories.map(cat => (
              <label key={cat.id} className="flex items-center gap-1 text-sm">
                <input
                  type="checkbox"
                  checked={selectedCategories.includes(cat.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedCategories([...selectedCategories, cat.id])
                    } else {
                      setSelectedCategories(selectedCategories.filter(id => id !== cat.id))
                    }
                  }}
                />
                {cat.name}
              </label>
            ))}
          </div>
        )}
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => setShowCategories(!showCategories)}
          className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
        >
          选择分类
        </button>
        <button
          onClick={() => onAdd(journal, selectedCategories)}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          添加
        </button>
      </div>
    </div>
  )
}
