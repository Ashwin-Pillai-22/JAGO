import { useState } from 'react'
import { GraduationCap, Landmark } from 'lucide-react'
import { useScholarships } from './useScholarships.js'

const emptyForm = {
  name: '',
  email: '',
  password: '',
  category: 'ST',
  state: '',
  income: '',
  education_level: 'Post-Matric',
  course: '',
}

export default function AuthPage({ onAuth }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const { items, status } = useScholarships()

  const update = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }))

  async function submit(event) {
    event.preventDefault()
    if (busy) return
    setError('')
    setBusy(true)
    try {
      const isRegister = mode === 'register'
      const payload = isRegister
        ? { ...form, income: Number(form.income) }
        : { email: form.email, password: form.password }
      const response = await fetch(`/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        const detail = Array.isArray(data.detail) ? 'Please check the details you entered.' : data.detail
        throw new Error(detail || 'Something went wrong. Try again.')
      }
      onAuth(data.token, data.student, form.email)
    } catch (err) {
      setError(err.message || 'Could not connect to the server.')
    } finally {
      setBusy(false)
    }
  }

  const isRegister = mode === 'register'

  return (
    <div className="auth-shell">
      <aside className="auth-left">
        <div className="brand">
          <span className="brand-mark"><Landmark size={20} strokeWidth={2.2} /></span>
          <span className="brand-name">JAGO<span>.</span></span>
        </div>
        <div className="auth-left-body">
          <span className="workspace-label">SCHOLARSHIPS FOR YOU</span>
          <h2>Find the scholarship that fits you.</h2>
          <ul className="auth-scholarships">
            {status === 'loading' && <li className="auth-muted">Loading scholarships...</li>}
            {status === 'error' && <li className="auth-muted">Scholarship list unavailable right now.</li>}
            {items.map((item) => (
              <li key={item.id}>
                <GraduationCap size={16} />
                <span>{item.name}</span>
              </li>
            ))}
          </ul>
        </div>
        <p className="auth-left-note">Answers are based on records currently available in JAGO.</p>
      </aside>

      <main className="auth-right">
        <form className="auth-card" onSubmit={submit}>
          <div className="auth-tabs" role="tablist">
            <button type="button" role="tab" aria-selected={!isRegister} className={!isRegister ? 'active' : ''} onClick={() => { setMode('login'); setError('') }}>Login</button>
            <button type="button" role="tab" aria-selected={isRegister} className={isRegister ? 'active' : ''} onClick={() => { setMode('register'); setError('') }}>Register</button>
          </div>
          <h1>{isRegister ? 'Create your account' : 'Welcome back'}</h1>

          {isRegister && (
            <label>Full name
              <input required value={form.name} onChange={update('name')} autoComplete="name" />
            </label>
          )}
          <label>Email
            <input required type="email" value={form.email} onChange={update('email')} autoComplete="email" />
          </label>
          <label>Password
            <input required type="password" minLength={6} value={form.password} onChange={update('password')} autoComplete={isRegister ? 'new-password' : 'current-password'} />
          </label>

          {isRegister && (
            <>
              <div className="auth-row">
                <label>Category
                  <select value={form.category} onChange={update('category')}>
                    <option>ST</option><option>SC</option><option>OBC</option><option>General</option>
                  </select>
                </label>
                <label>State
                  <input required value={form.state} onChange={update('state')} />
                </label>
              </div>
              <div className="auth-row">
                <label>Annual family income (₹)
                  <input required type="number" min="0" value={form.income} onChange={update('income')} />
                </label>
                <label>Education level
                  <select value={form.education_level} onChange={update('education_level')}>
                    <option>Pre-Matric</option><option>Post-Matric</option><option>Graduation</option><option>Post-Graduation</option><option>PhD</option>
                  </select>
                </label>
              </div>
              <label>Course
                <input required value={form.course} onChange={update('course')} />
              </label>
            </>
          )}

          {error && <p className="auth-error" role="alert">{error}</p>}
          <button className="auth-submit" type="submit" disabled={busy}>
            {busy ? 'Please wait...' : isRegister ? 'Create account' : 'Login'}
          </button>
        </form>
      </main>
    </div>
  )
}
