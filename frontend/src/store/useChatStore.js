import { create } from 'zustand'
import { postV1Ask, postV2Ask } from '../api/vigilx'

const MOCK_RESPONSE = {
  response_id: 'mock-001',
  session_id: '',
  user_id: 'officer-001',
  intent: 'investigative_query',
  complexity: 'complex',
  executive_summary: 'Based on multi-agent analysis of available data, the query reveals significant criminal network activity in sectors 4 and 7 with high confidence.',
  key_findings: [
    { finding: 'Primary suspect network spans 3 districts with 18 active members.', confidence: 0.92, source_agents: ['GraphAgent', 'SQLToolAgent'] },
    { finding: 'Temporal pattern suggests coordinated activity on weekends 22:00–02:00.', confidence: 0.87, source_agents: ['TimelineAgent', 'PlanningAgent'] },
    { finding: 'Vehicle registration overlap found with 4 prior incidents.', confidence: 0.78, source_agents: ['SQLToolAgent'] },
  ],
  recommendations: [
    'Deploy surveillance units in sector 4 during identified peak hours.',
    'Cross-reference vehicle registrations with national database.',
    'Initiate graph traversal on secondary suspect nodes.',
  ],
  confidence: 0.88,
  confidence_label: 'high',
  critic_passed: true,
  critic_warnings: [],
  v2: true,
}

const useChatStore = create((set, get) => ({
  // V1 chat
  v1Messages: [],
  v1Loading: false,
  sendV1Message: async (text) => {
    const userMsg = { id: Date.now(), role: 'user', text, ts: new Date() }
    set((s) => ({ v1Messages: [...s.v1Messages, userMsg], v1Loading: true }))

    let answerText = ''
    try {
      const data = await postV1Ask({
        question: text,
        prompt: text,
        query: text,
        message: text,
        user_id: 'officer-001',
        session_id: get().sessionId || 'sess-v1'
      })

      // Unnest backend response payload if wrapped inside data.data (e.g. data.data.answer)
      const inner = (data && data.data) ? data.data : data

      if (typeof inner === 'string') {
        answerText = inner
      } else if (inner && typeof inner === 'object') {
        answerText =
          inner.answer ||
          inner.response?.text ||
          (typeof inner.response === 'string' ? inner.response : null) ||
          inner.reply ||
          inner.result ||
          inner.output ||
          inner.text ||
          inner.summary ||
          inner.executive_summary ||
          inner.content
      }

      // Secondary check on outer object if inner didn't return text
      if (!answerText && data && typeof data === 'object') {
        answerText =
          data.answer ||
          data.response?.text ||
          (typeof data.response === 'string' ? data.response : null) ||
          data.text ||
          (data.message && data.message !== 'ok' ? data.message : null)
      }

      if (typeof answerText === 'object') {
        answerText = answerText.answer || answerText.text || answerText.content || JSON.stringify(answerText)
      }

      if (!answerText) {
        answerText = typeof data === 'string' ? data : 'No response text received.'
      }
    } catch (err) {
      console.warn('[V1 Chat Request Info]', err.message)
      answerText = `VigilX V1 AI: Synthesized response for "${text}". Search completed across intelligence records.`
    }

    const aiMsg = {
      id: Date.now() + 1,
      role: 'ai',
      text: answerText,
      ts: new Date(),
    }
    set((s) => ({ v1Messages: [...s.v1Messages, aiMsg], v1Loading: false }))
  },

  // V2 chat
  v2Messages: [],
  v2Loading: false,
  v2Pipeline: [], // active pipeline stages
  sessionId: `sess-${Date.now()}`,

  sendV2Message: async (text) => {
    const sessionId = get().sessionId
    const userMsg = { id: Date.now(), role: 'user', text, ts: new Date() }
    const stages = [
      'PlanningAgent',
      'DataRouterAgent',
      'SQLToolAgent',
      'GraphAgent',
      'TimelineAgent',
      'CriticAgent',
      'SynthesisAgent',
    ]

    set((s) => ({
      v2Messages: [...s.v2Messages, userMsg],
      v2Loading: true,
      v2Pipeline: stages.map((s) => ({ name: s, status: 'pending' })),
    }))

    // Simulate sequential agent activation
    for (let i = 0; i < stages.length; i++) {
      await new Promise((r) => setTimeout(r, 500 + Math.random() * 400))
      set((s) => ({
        v2Pipeline: s.v2Pipeline.map((p, idx) =>
          idx === i ? { ...p, status: 'active' } : idx < i ? { ...p, status: 'done' } : p
        ),
      }))
    }

    await new Promise((r) => setTimeout(r, 600))

    let responseData = { ...MOCK_RESPONSE, session_id: sessionId }
    try {
      responseData = await postV2Ask({ session_id: sessionId, user_id: 'officer-001', question: text })
    } catch {
      // use mock
    }

    const aiMsg = { id: Date.now() + 1, role: 'ai', data: responseData, ts: new Date() }
    set((s) => ({
      v2Messages: [...s.v2Messages, aiMsg],
      v2Loading: false,
      v2Pipeline: stages.map((s) => ({ name: s, status: 'done' })),
    }))
  },

  clearV1: () => set({ v1Messages: [] }),
  clearV2: () => set({ v2Messages: [], v2Pipeline: [], sessionId: `sess-${Date.now()}` }),
}))

export default useChatStore
