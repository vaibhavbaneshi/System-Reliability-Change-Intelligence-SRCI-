import { Search, FileText } from 'lucide-react'
import { useState } from 'react'

const articles = [
  { id: 1, title: 'Diagnosing Memory Leaks in Node.js Applications', category: 'runbook', views: 234, rating: 4.8 },
  { id: 2, title: 'Database Connection Pool Best Practices', category: 'playbook', views: 156, rating: 4.7 },
  { id: 3, title: 'Managing Database Failover Events', category: 'runbook', views: 312, rating: 4.9 },
  { id: 4, title: 'Incident Response for Payment Service Outages', category: 'playbook', views: 189, rating: 4.6 },
  { id: 5, title: 'API Rate Limiting Configuration Guide', category: 'guide', views: 267, rating: 4.8 },
]

export default function KnowledgeBase() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const filtered = articles.filter(a =>
    a.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
    (!selectedCategory || a.category === selectedCategory)
  )

  return (
    <div className="p-8 max-w-4xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Knowledge Base</h1>
        <p className="text-muted-foreground">Runbooks, playbooks, and incident response guides</p>
      </div>

      {/* Search */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search articles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-sm text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2">
        {['runbook', 'playbook', 'guide'].map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(selectedCategory === cat ? null : cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedCategory === cat
                ? 'bg-primary text-primary-foreground'
                : 'bg-card border border-border text-muted-foreground hover:text-foreground'
            }`}
          >
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      {/* Articles */}
      <div className="space-y-3">
        {filtered.map(article => (
          <a
            key={article.id}
            href="#"
            className="block bg-card border border-border rounded-lg p-4 hover:border-primary hover:shadow-lg transition-all group"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <FileText size={16} className="text-primary" />
                  <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                    {article.title}
                  </h3>
                  <span className="px-2 py-1 text-xs bg-muted/30 border border-muted rounded capitalize">
                    {article.category}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {article.views} views • Rating: {article.rating}/5
                </p>
              </div>
              <button className="px-4 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors text-sm font-medium">
                Read
              </button>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
