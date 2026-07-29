import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Bot, Copy, Check, ThumbsUp, ThumbsDown, RefreshCw, Volume2, Code } from 'lucide-react'

// Rich Text & Markdown parser for VigilX Conversational Responses
function FormattedContent({ text }) {
  if (!text) return null

  // Split by code blocks first
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g
  const parts = []
  let lastIndex = 0
  let match

  while ((match = codeBlockRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', content: text.slice(lastIndex, match.index) })
    }
    parts.push({ type: 'code', lang: match[1] || 'code', code: match[2].trim() })
    lastIndex = codeBlockRegex.lastIndex
  }
  if (lastIndex < text.length) {
    parts.push({ type: 'text', content: text.slice(lastIndex) })
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13, lineHeight: 1.6, color: 'var(--text-primary)' }}>
      {parts.map((part, idx) => {
        if (part.type === 'code') {
          return <CodeBlock key={idx} lang={part.lang} code={part.code} />
        }
        return <TextParagraphs key={idx} text={part.content} />
      })}
    </div>
  )
}

function CodeBlock({ lang, code }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div style={{
      background: '#070B14',
      border: '1px solid var(--border-dim)',
      borderRadius: 6,
      overflow: 'hidden',
      margin: '6px 0'
    }}>
      {/* Code Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justify: 'space-between',
        padding: '6px 12px',
        background: 'var(--bg-row)',
        borderBottom: '1px solid var(--border-dim)',
        fontFamily: 'var(--mono)',
        fontSize: 10,
        color: 'var(--text-tertiary)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Code size={11} style={{ color: 'var(--cyan)' }} />
          <span>{lang.toUpperCase()}</span>
        </div>
        <button
          onClick={handleCopy}
          style={{
            background: 'none',
            border: 'none',
            color: copied ? 'var(--green)' : 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            fontSize: 10,
            fontFamily: 'var(--mono)'
          }}
        >
          {copied ? <Check size={11} /> : <Copy size={11} />}
          <span>{copied ? 'Copied!' : 'Copy Code'}</span>
        </button>
      </div>

      {/* Code Content */}
      <pre style={{
        padding: '12px',
        margin: 0,
        fontFamily: 'var(--mono)',
        fontSize: 11,
        color: '#00C8F0',
        overflowX: 'auto',
        lineHeight: 1.5,
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-all'
      }}>
        {code}
      </pre>
    </div>
  )
}

function TextParagraphs({ text }) {
  const lines = text.split('\n')
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {lines.map((line, i) => {
        const trimmed = line.trim()
        if (!trimmed) return <div key={i} style={{ height: 4 }} />

        // Header ###
        if (trimmed.startsWith('### ')) {
          return (
            <h4 key={i} style={{ fontSize: 13, fontWeight: 700, color: 'var(--cyan)', margin: '8px 0 2px 0', fontFamily: 'var(--mono)', letterSpacing: '0.02em' }}>
              {trimmed.replace(/^###\s+/, '')}
            </h4>
          )
        }
        if (trimmed.startsWith('## ') || trimmed.startsWith('# ')) {
          return (
            <h3 key={i} style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', margin: '10px 0 4px 0', borderBottom: '1px solid var(--border-dim)', paddingBottom: 4 }}>
              {trimmed.replace(/^##?\s+/, '')}
            </h3>
          )
        }

        // Bullet point - or *
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          const content = trimmed.replace(/^[-*]\s+/, '')
          return (
            <div key={i} style={{ display: 'flex', gap: 8, paddingLeft: 4 }}>
              <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>•</span>
              <span style={{ flex: 1 }} dangerouslySetInnerHTML={{ __html: formatInline(content) }} />
            </div>
          )
        }

        // Numbered list (e.g., "1. ")
        if (/^\d+\.\s+/.test(trimmed)) {
          const num = trimmed.match(/^(\d+\.)\s+/)[1]
          const content = trimmed.replace(/^\d+\.\s+/, '')
          return (
            <div key={i} style={{ display: 'flex', gap: 8, paddingLeft: 4 }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--purple)', fontWeight: 600 }}>{num}</span>
              <span style={{ flex: 1 }} dangerouslySetInnerHTML={{ __html: formatInline(content) }} />
            </div>
          )
        }

        return (
          <p key={i} style={{ margin: 0 }} dangerouslySetInnerHTML={{ __html: formatInline(trimmed) }} />
        )
      })}
    </div>
  )
}

function formatInline(str) {
  if (!str) return ''
  return str
    .replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-primary); font-weight: 600;">$1</strong>')
    .replace(/`([^`]+)`/g, '<code style="font-family: var(--mono); font-size: 11px; background: var(--bg-row); border: 1px solid var(--border-dim); color: var(--cyan); padding: 1px 5px; border-radius: 3px;">$1</code>')
}

export default function VigilXFormattedResponse({ text, timestamp, onRegenerate }) {
  const [copied, setCopied] = useState(false)
  const [liked, setLiked] = useState(null)

  const handleCopyAll = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  const handleSpeak = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text.replace(/[*#`]/g, ''))
      utterance.rate = 1.0
      window.speechSynthesis.speak(utterance)
    }
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      maxWidth: 720,
      width: '100%',
      background: 'var(--bg-panel)',
      border: '1px solid var(--border-base)',
      borderRadius: 8,
      overflow: 'hidden',
      boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)',
      margin: '4px 0'
    }}>
      {/* Header bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justify: 'space-between',
        padding: '8px 14px',
        background: 'var(--bg-row)',
        borderBottom: '1px solid var(--border-dim)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 22,
            height: 22,
            borderRadius: 5,
            background: 'linear-gradient(135deg, #00C8F0, #8B5CF6)',
            display: 'flex',
            alignItems: 'center',
            justify: 'center'
          }}>
            <Bot size={12} style={{ color: '#000' }} />
          </div>
          <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
            VigilX Intelligence AI
          </span>
          <span className="tag-cyan" style={{ fontSize: 9, padding: '1px 6px' }}>
            VigilX Core AI
          </span>
        </div>

        {timestamp && (
          <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: 'var(--text-tertiary)' }}>
            {new Date(timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </div>

      {/* Content Body */}
      <div style={{ padding: '14px 16px' }}>
        <FormattedContent text={text} />
      </div>

      {/* Interactive Action Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justify: 'space-between',
        padding: '6px 14px',
        background: 'var(--bg-row)',
        borderTop: '1px solid var(--border-dim)',
        fontSize: 11
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Copy Button */}
          <button
            onClick={handleCopyAll}
            title="Copy Response"
            style={{
              background: 'none',
              border: 'none',
              color: copied ? 'var(--green)' : 'var(--text-tertiary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              fontSize: 10,
              fontFamily: 'var(--mono)'
            }}
          >
            {copied ? <Check size={11} style={{ color: 'var(--green)' }} /> : <Copy size={11} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          {/* Read Aloud */}
          <button
            onClick={handleSpeak}
            title="Read Aloud"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-tertiary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              fontSize: 10,
              fontFamily: 'var(--mono)'
            }}
          >
            <Volume2 size={11} />
            <span>Listen</span>
          </button>

          {/* Regenerate */}
          {onRegenerate && (
            <button
              onClick={onRegenerate}
              title="Regenerate Response"
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-tertiary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                fontSize: 10,
                fontFamily: 'var(--mono)'
              }}
            >
              <RefreshCw size={11} />
              <span>Retry</span>
            </button>
          )}
        </div>

        {/* Feedback Icons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            onClick={() => setLiked(liked === 'up' ? null : 'up')}
            style={{
              background: 'none',
              border: 'none',
              color: liked === 'up' ? 'var(--green)' : 'var(--text-tertiary)',
              cursor: 'pointer'
            }}
          >
            <ThumbsUp size={11} />
          </button>
          <button
            onClick={() => setLiked(liked === 'down' ? null : 'down')}
            style={{
              background: 'none',
              border: 'none',
              color: liked === 'down' ? 'var(--red)' : 'var(--text-tertiary)',
              cursor: 'pointer'
            }}
          >
            <ThumbsDown size={11} />
          </button>
        </div>
      </div>
    </div>
  )
}
