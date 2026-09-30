import { useEffect, useRef, useState } from 'react'
import {
  ArrowUp,
  BookOpenText,
  CircleHelp,
  FileCheck2,
  GraduationCap,
  Eye,
  Landmark,
  LogOut,
  MapPin,
  UserRound,
  RotateCcw,
  ShieldCheck,
  WalletCards,
} from 'lucide-react'
import AuthPage from './AuthPage.jsx'
import { ScholarshipList } from './ScholarshipList.jsx'
import './App.css'

const starterMessage = {
  id: 'welcome',
  role: 'assistant',
  text: 'Namaste. I can help you explore scholarships using the information available in JAGO.',
}

const suggestions = [
  { label: 'Check my eligibility', message: 'Am I eligible for a scholarship?', icon: ShieldCheck },
  { label: 'Browse scholarships', message: 'Which scholarships are available?', icon: GraduationCap },
  { label: 'Required documents', message: 'What documents do I need?', icon: FileCheck2 },
  { label: 'Payment information', message: 'When will I get my payment?', icon: WalletCards },
]

const intentLabels = {
  CHECK_ELIGIBILITY: 'Eligibility',
  LIST_SCHOLARSHIPS: 'Scholarships',
  REQUIRED_DOCUMENTS: 'Documents',
  APPLICATION_STATUS: 'Application status',
  DISBURSEMENT: 'Payments',
  STATISTICS: 'Statistics',
  UNKNOWN: 'General question',
}

const profileFields = [
  { label: 'Student ID', key: 'id' },
  { label: 'Full name', key: 'name' },
  { label: 'Email', key: 'email' },
  { label: 'Category', key: 'category' },
  { label: 'State', key: 'state' },
  { label: 'Annual family income', key: 'income', format: (value) => `₹${Number(value).toLocaleString('en-IN')}` },
  { label: 'Education level', key: 'education_level' },
  { label: 'Course', key: 'course' },
]

const documentTypes = [
  { key: 'aadhaar', label: 'Aadhaar card' },
  { key: 'domicile', label: 'Domicile certificate' },
  { key: 'caste', label: 'Caste certificate' },
  { key: 'marksheet_10', label: '10th marksheet' },
  { key: 'marksheet_12', label: '12th marksheet' },
  { key: 'graduation', label: 'Graduation degree' },
  { key: 'post_graduation', label: 'Post-graduation degree' },
]

function Profile({ user, token }) {
  const [documents, setDocuments] = useState([])
  const [documentStatus, setDocumentStatus] = useState('loading')
  const [uploading, setUploading] = useState('')
  const [uploadError, setUploadError] = useState('')

  useEffect(() => {
    const controller = new AbortController()
    fetch(`/api/students/${user.id}/documents`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) throw new Error('Could not load documents')
        return response.json()
      })
      .then((data) => {
        setDocuments(data)
        setDocumentStatus('ready')
      })
      .catch(() => {
        if (!controller.signal.aborted) setDocumentStatus('error')
      })
    return () => controller.abort()
  }, [token, user.id])

  async function uploadDocument(documentType, file) {
    if (!file) return
    setUploading(documentType)
    setUploadError('')
    const body = new FormData()
    body.append('document_type', documentType)
    body.append('file', file)
    try {
      const response = await fetch(`/api/students/${user.id}/documents`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body,
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(data.detail || 'Could not upload document')
      setDocuments((current) => [data, ...current.filter((item) => item.document_type !== documentType)])
    } catch (error) {
      setUploadError(error.message)
    } finally {
      setUploading('')
    }
  }

  return (
    <section className="profile-area" aria-label="Your profile">
      <div className="profile-hero">
        <div className="profile-avatar"><UserRound size={29} /></div>
        <div>
          <span className="section-kicker">YOUR JAGO PROFILE</span>
          <h2>{user.name}</h2>
          <p>Your scholarship details, all in one place.</p>
        </div>
      </div>

      <div className="profile-card">
        <div className="profile-card-heading">
          <div>
            <span className="workspace-label">PERSONAL DETAILS</span>
            <h3>Student information</h3>
          </div>
          <span className="profile-status"><span />Profile active</span>
        </div>
        <div className="profile-grid">
          {profileFields.map(({ label, key, format }) => (
            <div className="profile-field" key={key}>
              <span>{label}</span>
              <strong>{format ? format(user[key]) : user[key] || 'Not provided'}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="profile-note">
        <MapPin size={16} />
        <p>Your profile helps JAGO find scholarships that match your category, location, income, and education.</p>
      </div>

      <div className="profile-card documents-card">
        <div className="profile-card-heading">
          <div>
            <span className="workspace-label">REQUIRED DOCUMENTS</span>
            <h3>Upload your documents</h3>
          </div>
          <span className="documents-hint">PDF, PNG or JPEG · 10 MB max</span>
        </div>
        {documentStatus === 'error' && <p className="document-error">Could not load your documents. Try refreshing the page.</p>}
        {uploadError && <p className="document-error" role="alert">{uploadError}</p>}
        <div className="document-list">
          {documentTypes.map(({ key, label }) => {
            const document = documents.find((item) => item.document_type === key)
            return (
              <div className="document-row" key={key}>
                <div className="document-copy">
                  <strong>{label}</strong>
                  <span>{document ? document.filename : 'Not uploaded yet'}</span>
                </div>
                <div className="document-actions">
                  {document && (
                    <a
                      className="document-view"
                      href={`/api/students/${user.id}/documents/${document.id}`}
                      rel="noreferrer"
                      target="_blank"
                    >
                      <Eye size={14} />
                      <span>Show</span>
                    </a>
                  )}
                  <label className={`document-upload${uploading === key ? ' document-uploading' : ''}`}>
                    <input
                      accept=".pdf,.png,.jpg,.jpeg"
                      disabled={Boolean(uploading)}
                      onChange={(event) => uploadDocument(key, event.target.files[0])}
                      type="file"
                    />
                    {uploading === key ? 'Uploading...' : document ? 'Replace' : 'Upload'}
                  </label>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

function Dashboard({ user, token, onLogout }) {
  const studentId = String(user.id)
  const [view, setView] = useState('chat')
  const [draft, setDraft] = useState('')
  const [messages, setMessages] = useState([starterMessage])
  const [pending, setPending] = useState(false)
  const [connection, setConnection] = useState('checking')
  const conversationEnd = useRef(null)

  useEffect(() => {
    const controller = new AbortController()
    fetch('/api/health', { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error('Backend unavailable')
        return response.json()
      })
      .then(() => setConnection('online'))
      .catch(() => {
        if (!controller.signal.aborted) setConnection('offline')
      })
    return () => controller.abort()
  }, [])

  useEffect(() => {
    conversationEnd.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, pending])

  async function sendMessage(message = draft) {
    const cleanMessage = message.trim()
    const numericStudentId = Number(studentId)
    if (!cleanMessage || pending) return
    if (!Number.isInteger(numericStudentId) || numericStudentId < 1) {
      setMessages((current) => [
        ...current,
        {
          id: Date.now(),
          role: 'assistant',
          text: 'Enter a valid student ID before sending your question.',
        },
      ])
      return
    }

    setMessages((current) => [
      ...current,
      { id: `${Date.now()}-user`, role: 'user', text: cleanMessage },
    ])
    setDraft('')
    setPending(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: numericStudentId, message: cleanMessage }),
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(data.detail || 'JAGO could not process that request.')
      }
      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-assistant`,
          role: 'assistant',
          text: data.response,
          intent: data.intent,
        },
      ])
      setConnection('online')
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: `${Date.now()}-error`,
          role: 'assistant',
          text: error.message || 'Could not connect to JAGO. Check that the backend is running.',
          error: true,
        },
      ])
      setConnection('offline')
    } finally {
      setPending(false)
    }
  }

  function handleSubmit(event) {
    event.preventDefault()
    sendMessage()
  }

  function resetConversation() {
    setMessages([starterMessage])
    setDraft('')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#main" aria-label="JAGO home">
          <span className="brand-mark"><Landmark size={20} strokeWidth={2.2} /></span>
          <span className="brand-name">JAGO<span>.</span></span>
        </a>

        <div className="sidebar-rule" />
        <div className="workspace-label">YOUR WORKSPACE</div>
        <button className={`nav-item${view === 'scholarships' ? ' nav-item-active' : ''}`} onClick={() => setView('scholarships')} type="button">
          <GraduationCap size={17} />
          <span>Scholarships</span>
        </button>
        <button className={`nav-item${view === 'chat' ? ' nav-item-active' : ''}`} onClick={() => setView('chat')} type="button">
          <BookOpenText size={17} />
          <span>Scholarship assistant</span>
        </button>
        <button className={`nav-item${view === 'profile' ? ' nav-item-active' : ''}`} onClick={() => setView('profile')} type="button">
          <UserRound size={17} />
          <span>My profile</span>
        </button>

        <div className="sidebar-bottom">
          <div className="help-mark"><CircleHelp size={17} /></div>
          <p>Answers are based on records currently available in JAGO.</p>
        </div>
      </aside>

      <main className="main-panel" id="main">
        <header className="topbar">
          <div className="page-title">
            <span className="eyebrow">ST SCHOLARSHIP SUPPORT</span>
            <h1>{view === 'chat' ? 'Scholarship assistant' : view === 'scholarships' ? 'Scholarships' : 'My profile'}</h1>
          </div>
          <div className="topbar-tools">
            <div className={`connection-status connection-${connection}`}>
              <span className="status-dot" />
              {connection === 'checking' ? 'Connecting' : connection === 'online' ? 'Backend connected' : 'Backend offline'}
            </div>
            <span className="user-chip">{user.name}</span>
            <button className="reset-button" onClick={onLogout} type="button">
              <LogOut size={15} />
              <span>Logout</span>
            </button>
          </div>
        </header>

        {view === 'scholarships' ? <ScholarshipList /> : view === 'profile' ? <Profile user={user} token={token} /> : (
        <section className="chat-area" aria-label="Scholarship chat">
          <div className="chat-heading">
            <div>
              <span className="section-kicker">YOUR JAGO GUIDE</span>
              <h2>What would you like to know?</h2>
            </div>
            <button
              className="reset-button"
              onClick={resetConversation}
              title="Start a new conversation"
              type="button"
            >
              <RotateCcw size={15} />
              <span>New chat</span>
            </button>
          </div>

          <div className="conversation" aria-live="polite" aria-relevant="additions text">
            {messages.map((message) => (
              <article className={`message-row message-${message.role}`} key={message.id}>
                {message.role === 'assistant' && (
                  <span className="assistant-avatar"><Landmark size={16} /></span>
                )}
                <div className={`message-content${message.error ? ' message-error' : ''}`}>
                  {message.intent && (
                    <span className="intent-label">{intentLabels[message.intent] || 'JAGO response'}</span>
                  )}
                  <p>{message.text}</p>
                </div>
              </article>
            ))}
            {pending && (
              <div className="message-row message-assistant">
                <span className="assistant-avatar"><Landmark size={16} /></span>
                <div className="message-content typing-indicator" aria-label="JAGO is responding">
                  <span /><span /><span />
                </div>
              </div>
            )}
            <div ref={conversationEnd} />
          </div>

          {messages.length === 1 && (
            <div className="suggestion-grid" aria-label="Suggested questions">
              {suggestions.map(({ label, message, icon: Icon }) => (
                <button
                  className="suggestion-button"
                  key={label}
                  onClick={() => sendMessage(message)}
                  type="button"
                >
                  <Icon size={17} />
                  <span>{label}</span>
                </button>
              ))}
            </div>
          )}

          <form className="composer" onSubmit={handleSubmit}>
            <input
              aria-label="Your question"
              autoComplete="off"
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask about scholarships, documents, or payments..."
              value={draft}
            />
            <button
              aria-label="Send message"
              className="send-button"
              disabled={!draft.trim() || pending}
              title="Send message"
              type="submit"
            >
              <ArrowUp size={19} strokeWidth={2.4} />
            </button>
          </form>
          <p className="disclaimer">JAGO uses available records only. Confirm eligibility with the official scheme authority.</p>
        </section>
        )}
      </main>
    </div>
  )
}

function App() {
  const [session, setSession] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('jago-session')) || null
    } catch {
      return null
    }
  })

  useEffect(() => {
    if (!session) return
    fetch('/api/auth/me', { headers: { Authorization: `Bearer ${session.token}` } })
      .then(async (response) => {
        if (response.status === 401) logout()
        if (!response.ok) return
        const student = await response.json()
        const next = { ...session, student }
        localStorage.setItem('jago-session', JSON.stringify(next))
        setSession(next)
      })
      .catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function login(token, student, email) {
    const next = { token, student: { ...student, email: email.trim().toLowerCase() } }
    localStorage.setItem('jago-session', JSON.stringify(next))
    setSession(next)
  }

  function logout() {
    localStorage.removeItem('jago-session')
    setSession(null)
  }

  if (!session) return <AuthPage onAuth={login} />
  return <Dashboard user={session.student} token={session.token} onLogout={logout} />
}

export default App
