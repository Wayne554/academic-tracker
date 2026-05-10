import React, { useState } from 'react'

export default function Sidebar({ journals, categories, filters, setFilters }) {
  const [categoriesOpen, setCategoriesOpen] = useState(true)
  const [journalsOpen, setJournalsOpen] = useState(true)

  const journalsByCategory = {}
  categories.forEach(cat => {
    journalsByCategory[cat.id] = journals.filter(j =>
      j.categories?.some(c => c.id === cat.id)
    )
  })
  const uncategorizedJournals = journals.filter(j =>
    !j.categories || j.categories.length === 0
  )

  return (
    <aside className="w-64 bg-white border-r h-[calc(100vh-4rem)] overflow-y-auto hidden md:block">
      <div className="p-4 space-y-4">
        <button
          onClick={() => setFilters(f => ({ ...f, category_id: null, journal_id: null }))}
          className={`w-full text-left px-3 py-2 rounded-lg text-sm ${
            !filters.category_id && !filters.journal_id
              ? 'bg-blue-50 text-blue-700'
              : 'hover:bg-gray-50'
          }`}
        >
          全部论文
        </button>

        <div>
          <button
            onClick={() => setCategoriesOpen(!categoriesOpen)}
            className="flex items-center justify-between w-full px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg"
          >
            分类
            <svg className={`w-4 h-4 transition-transform ${categoriesOpen ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          {categoriesOpen && (
            <div className="mt-1 ml-2 space-y-1">
              {categories.map(category => (
                <button
                  key={category.id}
                  onClick={() => setFilters(f => ({ ...f, category_id: category.id, journal_id: null }))}
                  className={`w-full text-left px-3 py-1.5 rounded text-sm ${
                    filters.category_id === category.id
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {category.name}
                </button>
              ))}
            </div>
          )}
        </div>

        <div>
          <button
            onClick={() => setJournalsOpen(!journalsOpen)}
            className="flex items-center justify-between w-full px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg"
          >
            期刊
            <svg className={`w-4 h-4 transition-transform ${journalsOpen ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          {journalsOpen && (
            <div className="mt-1 ml-2 space-y-2">
              {categories.map(category => (
                journalsByCategory[category.id]?.length > 0 && (
                  <div key={category.id} className="space-y-1">
                    <div className="text-xs text-gray-500 px-3 py-1">{category.name}</div>
                    {journalsByCategory[category.id].map(journal => (
                      <button
                        key={journal.id}
                        onClick={() => setFilters(f => ({ ...f, journal_id: journal.id, category_id: null }))}
                        className={`w-full text-left px-3 py-1.5 rounded text-sm truncate ${
                          filters.journal_id === journal.id
                            ? 'bg-blue-50 text-blue-700'
                            : 'text-gray-600 hover:bg-gray-50'
                        }`}
                      >
                        {journal.display_name}
                      </button>
                    ))}
                  </div>
                )
              ))}
              {uncategorizedJournals.length > 0 && (
                <div className="space-y-1">
                  <div className="text-xs text-gray-500 px-3 py-1">未分类</div>
                  {uncategorizedJournals.map(journal => (
                    <button
                      key={journal.id}
                      onClick={() => setFilters(f => ({ ...f, journal_id: journal.id, category_id: null }))}
                      className={`w-full text-left px-3 py-1.5 rounded text-sm truncate ${
                        filters.journal_id === journal.id
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {journal.display_name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}
