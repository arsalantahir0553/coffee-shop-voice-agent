import { useEffect, useRef, useState } from 'react'

const STATUS_LABEL = {
  idle: 'Press the button to order',
  listening: 'Listening...',
  thinking: 'Thinking...',
  speaking: 'Speaking...',
}

export default function App() {
  const [state, setState] = useState({
    shop_name: 'Loading...',
    status: 'idle',
    busy: false,
    transcript: [],
    order: [],
    total: 0,
  })
  const transcriptRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    const poll = async () => {
      try {
        const res = await fetch('/api/state')
        const data = await res.json()
        if (!cancelled) setState(data)
      } catch (e) {
        // backend not reachable yet - ignore and retry on next tick
      }
    }
    poll()
    const id = setInterval(poll, 600)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight
    }
  }, [state.transcript])

  const startTurn = () => {
    fetch('/api/turn', { method: 'POST' })
  }

  const newOrder = () => {
    fetch('/api/reset', { method: 'POST' })
  }

  return (
    <div className="kiosk">
      <header className="kiosk-header">
        <h1>{state.shop_name}</h1>
        <span className={`status status-${state.status}`}>{STATUS_LABEL[state.status]}</span>
      </header>

      <main className="kiosk-body">
        <section className="transcript-panel">
          <h2>Conversation</h2>
          <div className="transcript" ref={transcriptRef}>
            {state.transcript.length === 0 && (
              <p className="empty">Press &ldquo;Order Now&rdquo; and speak when you hear &ldquo;Listening...&rdquo;</p>
            )}
            {state.transcript.map((m, i) => (
              <p key={i} className={m.speaker === 'You' ? 'msg you' : 'msg agent'}>
                <strong>{m.speaker}:</strong> {m.text}
              </p>
            ))}
          </div>
        </section>

        <aside className="order-panel">
          <h2>Current Order</h2>
          <div className="order-list">
            {state.order.length === 0 && <p className="empty">No items yet.</p>}
            {state.order.map((line, i) => (
              <p key={i} className="order-item">{line}</p>
            ))}
          </div>
          <div className="total">Total: ${Number(state.total).toFixed(2)}</div>
        </aside>
      </main>

      <footer className="kiosk-footer">
        <button className="btn-order" disabled={state.busy} onClick={startTurn}>
          {state.busy ? 'Working...' : 'Order Now'}
        </button>
        <button className="btn-reset" disabled={state.busy} onClick={newOrder}>
          New Order
        </button>
      </footer>
    </div>
  )
}
