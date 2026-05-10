import React, { useState } from 'react'

export default function PaperCard({ paper, onStar, onMarkRead }) {
  const [showAbstract, setShowAbstract] = useState(false)

  const authorNames = paper.authors?.map(a => a.name).join(', ') || ''
  const journalName = paper.journal?.display_name || ''
  const pubInfo = [
    journalName,
    paper.volume && `Vol. ${paper.volume}`,
    paper.issue && `No. ${paper.issue}`,
    paper.publication_date
  ].filter(Boolean).join(' | ')

  const getLink = () => {
    if (paper.landing_page_url) return paper.landing_page_url
    if (paper.doi) {
      if (paper.doi.startsWith('http')) return paper.doi
      return `https://doi.org/${paper.doi}`
    }
    return null
  }

  const link = getLink()

  return (
    <div className={`bg-white rounded-lg shadow p-4 ${!paper.is_read ? 'border-l-4 border-blue-500' : ''}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-2">
            {link ? (
              <a
                href={link}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => !paper.is_read && onMarkRead(paper.id)}
                className="text-lg font-semibold text-blue-600 hover:text-blue-800 hover:underline"
              >
                {paper.title}
              </a>
            ) : (
              <h3 className="text-lg font-semibold text-gray-900">{paper.title}</h3>
            )}
          </div>
          <div className="mt-1 text-sm text-gray-600">
            {authorNames}
          </div>
          <div className="mt-1 text-sm text-gray-500">
            {pubInfo}
          </div>
          {paper.abstract && (
            <div className="mt-2">
              <button
                onClick={() => setShowAbstract(!showAbstract)}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                {showAbstract ? '收起摘要' : '显示摘要'}
              </button>
              {showAbstract && (
                <p className="mt-2 text-sm text-gray-700 whitespace-pre-wrap">
                  {paper.abstract}
                </p>
              )}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={() => !paper.is_read && onMarkRead(paper.id)}
            className={`p-2 rounded-full ${paper.is_read ? 'text-gray-300' : 'text-blue-500 hover:bg-blue-50'}`}
            title={paper.is_read ? '已读' : '标记为已读'}
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </button>
          <button
            onClick={() => onStar(paper.id)}
            className={`p-2 rounded-full ${paper.is_starred ? 'text-yellow-500' : 'text-gray-400 hover:bg-yellow-50'}`}
            title={paper.is_starred ? '取消星标' : '添加星标'}
          >
            <svg className="w-5 h-5" fill={paper.is_starred ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
