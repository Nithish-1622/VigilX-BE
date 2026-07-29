import { useEffect, useRef } from 'react'

export default function ParticleNetwork({ style }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationFrameId
    let width = 0
    let height = 0
    let dpr = 1

    const mouse = { x: -1000, y: -1000, active: false }

    const handleMouseMove = (e) => {
      mouse.x = e.clientX
      mouse.y = e.clientY
      mouse.active = true
    }

    const handleMouseLeave = () => {
      mouse.active = false
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseleave', handleMouseLeave)

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2)
      width = window.innerWidth
      height = window.innerHeight
      canvas.width = width * dpr
      canvas.height = height * dpr
      canvas.style.width = `${width}px`
      canvas.style.height = `${height}px`
      ctx.scale(dpr, dpr)
    }

    resize()
    window.addEventListener('resize', resize)

    // Particle pool setup
    const particleCount = Math.min(Math.floor((width * height) / 9000), 160)
    const particles = []

    const colors = ['#00f0c8', '#00c8f0', '#38bdf8', '#8b5cf6', '#0284c7']

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.65,
        vy: (Math.random() - 0.5) * 0.65,
        radius: Math.random() * 2.2 + 1.0,
        color: colors[Math.floor(Math.random() * colors.length)],
        alpha: Math.random() * 0.6 + 0.4,
        pulseSpeed: 0.02 + Math.random() * 0.03,
        pulseAngle: Math.random() * Math.PI * 2,
      })
    }

    const maxDist = 140
    const mouseRadius = 180

    const render = () => {
      ctx.clearRect(0, 0, width, height)

      // Update particle positions
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i]

        p.x += p.vx
        p.y += p.vy

        // Wrap around boundaries
        if (p.x < -20) p.x = width + 20
        if (p.x > width + 20) p.x = -20
        if (p.y < -20) p.y = height + 20
        if (p.y > height + 20) p.y = -20

        // Pulse size & alpha
        p.pulseAngle += p.pulseSpeed
        const currentAlpha = p.alpha * (0.7 + Math.sin(p.pulseAngle) * 0.3)

        // Mouse repulsion / interaction
        if (mouse.active) {
          const dx = p.x - mouse.x
          const dy = p.y - mouse.y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < mouseRadius && dist > 0) {
            const force = (mouseRadius - dist) / mouseRadius
            p.x += (dx / dist) * force * 2.5
            p.y += (dy / dist) * force * 2.5
          }
        }

        // Draw particle dot
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
        ctx.fillStyle = p.color
        ctx.globalAlpha = currentAlpha
        ctx.fill()
      }

      // Draw network line connections & geometric mesh triangles
      ctx.lineWidth = 0.9

      for (let i = 0; i < particles.length; i++) {
        const p1 = particles[i]

        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j]
          const dx = p1.x - p2.x
          const dy = p1.y - p2.y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < maxDist) {
            const lineAlpha = (1 - dist / maxDist) * 0.38
            ctx.beginPath()
            ctx.moveTo(p1.x, p1.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.strokeStyle = `rgba(0, 240, 200, ${lineAlpha})`
            ctx.globalAlpha = lineAlpha
            ctx.stroke()

            // Connect third nearby node to form geometric mesh triangle
            for (let k = j + 1; k < particles.length; k++) {
              const p3 = particles[k]
              const d2 = Math.hypot(p2.x - p3.x, p2.y - p3.y)
              const d3 = Math.hypot(p1.x - p3.x, p1.y - p3.y)

              if (d2 < maxDist && d3 < maxDist) {
                const triAlpha = (1 - (dist + d2 + d3) / (maxDist * 3)) * 0.08
                ctx.beginPath()
                ctx.moveTo(p1.x, p1.y)
                ctx.lineTo(p2.x, p2.y)
                ctx.lineTo(p3.x, p3.y)
                ctx.closePath()
                ctx.fillStyle = `rgba(0, 200, 240, ${triAlpha})`
                ctx.globalAlpha = triAlpha
                ctx.fill()
                break
              }
            }
          }
        }

        // Draw line connections to cursor when mouse is active
        if (mouse.active) {
          const mdx = p1.x - mouse.x
          const mdy = p1.y - mouse.y
          const mdist = Math.sqrt(mdx * mdx + mdy * mdy)
          if (mdist < mouseRadius) {
            const mAlpha = (1 - mdist / mouseRadius) * 0.45
            ctx.beginPath()
            ctx.moveTo(p1.x, p1.y)
            ctx.lineTo(mouse.x, mouse.y)
            ctx.strokeStyle = `rgba(0, 200, 240, ${mAlpha})`
            ctx.globalAlpha = mAlpha
            ctx.stroke()
          }
        }
      }

      ctx.globalAlpha = 1.0
      animationFrameId = requestAnimationFrame(render)
    }

    render()

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseleave', handleMouseLeave)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <div style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', overflow: 'hidden', ...style }}>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} />
    </div>
  )
}
