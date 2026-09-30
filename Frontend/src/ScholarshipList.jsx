import { GraduationCap } from 'lucide-react'
import { useScholarships } from './useScholarships.js'

export function ScholarshipList() {
  const { items, status } = useScholarships()

  return (
    <section className="chat-area" aria-label="Scholarships">
      <div className="chat-heading">
        <div>
          <span className="section-kicker">AVAILABLE SCHEMES</span>
          <h2>Scholarships</h2>
        </div>
      </div>
      {status === 'loading' && <p className="muted">Loading scholarships...</p>}
      {status === 'error' && <p className="muted">Could not load scholarships. Check that the backend is running.</p>}
      <div className="scholarship-grid">
        {items.map((item) => (
          <article className="scholarship-card" key={item.id}>
            <span className="scholarship-icon"><GraduationCap size={18} /></span>
            <h3>{item.name}</h3>
            <p>{item.description || `${item.scheme} for ${item.category || 'eligible'} students.`}</p>
            <div className="scholarship-tags">
              {item.category && <span>{item.category}</span>}
              {item.education_level && <span>{item.education_level}</span>}
              {item.max_income != null && <span>Income up to ₹{item.max_income.toLocaleString('en-IN')}</span>}
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
