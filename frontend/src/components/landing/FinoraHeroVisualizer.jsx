import { useState, useEffect, useRef } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { BarChart3, Settings, PieChart, ShieldCheck, Cpu } from 'lucide-react'

export default function FinoraHeroVisualizer({ style }) {
  const containerRef = useRef(null)

  // Motion values for smooth 3D cursor perspective tilt
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  // Smooth spring physics for 3D tilt
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [10, -10]), { stiffness: 140, damping: 18 })
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-12, 12]), { stiffness: 140, damping: 18 })

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!containerRef.current) return
      const rect = containerRef.current.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width - 0.5
      const y = (e.clientY - rect.top) / rect.height - 0.5
      mouseX.set(x)
      mouseY.set(y)
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [mouseX, mouseY])

  return (
    <div
      ref={containerRef}
      style={{
        position: 'relative',
        width: '100%',
        height: 580,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        perspective: 1000,
        overflow: 'visible',
        ...style
      }}
    >
      {/* ── Background Volumetric Deep Purple & Cyan Stage Glow ────────────── */}
      <div
        style={{
          position: 'absolute', top: '55%', left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 480, height: 480,
          background: 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.48) 0%, rgba(0, 200, 240, 0.25) 50%, transparent 80%)',
          filter: 'blur(65px)', pointerEvents: 'none', zIndex: 0
        }}
      />

      {/* ── Interactive 3D Perspective Tilt Stage Container ───────────────── */}
      <motion.div
        style={{
          position: 'relative',
          width: 520,
          height: 480,
          rotateX,
          rotateY,
          transformStyle: 'preserve-3d',
          zIndex: 1
        }}
      >

        {/* Vertical Light Projection Cone Beam */}
        <div
          style={{
            position: 'absolute', top: 20, left: '50%', transform: 'translateX(-50%)',
            width: 190, height: 230,
            background: 'linear-gradient(to top, rgba(0, 200, 240, 0.4) 0%, rgba(139, 92, 246, 0.22) 60%, transparent 100%)',
            clipPath: 'polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%)',
            pointerEvents: 'none', zIndex: 1
          }}
        />

        {/* Floating 3D Data Tokens hovering in vertical light beam */}
        <motion.div
          animate={{ y: [-6, 6, -6] }}
          transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            position: 'absolute', top: 35, left: '46%', transform: 'translateX(-50%) translateZ(45px)',
            width: 38, height: 18, borderRadius: 20,
            background: 'linear-gradient(135deg, #00C8F0, #8B5CF6)',
            border: '1.5px solid rgba(255, 255, 255, 0.7)',
            boxShadow: '0 0 20px rgba(0, 200, 240, 0.9)', zIndex: 3
          }}
        />
        <motion.div
          animate={{ y: [6, -6, 6] }}
          transition={{ duration: 4.2, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
          style={{
            position: 'absolute', top: 75, left: '54%', transform: 'translateX(-50%) translateZ(45px)',
            width: 34, height: 16, borderRadius: 20,
            background: 'linear-gradient(135deg, #10B981, #00C8F0)',
            border: '1.5px solid rgba(255, 255, 255, 0.7)',
            boxShadow: '0 0 18px rgba(16, 185, 129, 0.9)', zIndex: 3
          }}
        />

        {/* ── STRAIGHT UPRIGHT FLOATING VIGILX CORE (Facing Front Straight) ─── */}
        <motion.div
          animate={{ y: [-8, 8, -8] }}
          transition={{ duration: 3.8, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            position: 'absolute', top: 110, left: '50%', transform: 'translateX(-50%) translateZ(80px)',
            width: 140, height: 118, borderRadius: 18,
            background: 'linear-gradient(135deg, rgba(12, 28, 48, 0.98), rgba(8, 16, 32, 0.98))',
            border: '2px solid #00C8F0',
            boxShadow: '0 0 45px rgba(0, 200, 240, 0.75), inset 0 0 25px rgba(0, 200, 240, 0.45)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 6,
            zIndex: 6
          }}
        >
          <Cpu size={44} style={{ color: '#00C8F0', filter: 'drop-shadow(0 0 16px #00C8F0)' }} />
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 12, fontWeight: 800, color: '#FFFFFF', letterSpacing: '0.12em' }}>
            VIGILX CORE
          </span>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '2px 8px', borderRadius: 10 }}>
            ● ACTIVE ENGINE
          </span>
        </motion.div>

        {/* Central Core Pure CSS 3D Isometric Base Platform (Below Core) */}
        <div
          style={{
            position: 'absolute', top: 200, left: '50%', transform: 'translateX(-50%) rotateX(60deg) rotateZ(-45deg)',
            width: 200, height: 200, borderRadius: 32,
            background: 'linear-gradient(135deg, rgba(12, 28, 48, 0.96), rgba(8, 16, 32, 0.98))',
            border: '2px solid rgba(0, 200, 240, 0.65)',
            boxShadow: '0 0 50px rgba(0, 200, 240, 0.55), inset 0 0 30px rgba(0, 200, 240, 0.35)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2
          }}
        />

        {/* ── SVG Connecting Vector Laser Paths ────────────────────────────── */}
        <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 1 }}>
          <line x1="130" y1="90" x2="260" y2="210" stroke="rgba(0, 200, 240, 0.55)" strokeWidth="1.5" strokeDasharray="4 3" />
          <line x1="390" y1="90" x2="260" y2="210" stroke="rgba(139, 92, 246, 0.55)" strokeWidth="1.5" strokeDasharray="4 3" />
          <line x1="130" y1="360" x2="260" y2="280" stroke="rgba(16, 185, 129, 0.55)" strokeWidth="1.5" strokeDasharray="4 3" />
          <line x1="390" y1="360" x2="260" y2="280" stroke="rgba(56, 189, 248, 0.55)" strokeWidth="1.5" strokeDasharray="4 3" />
        </svg>

        {/* ── 4 Translucent Floating Glass Badges Overlay (Upscaled) ─────────── */}

        {/* NODE 1 (Top-Left): Real-time Analytics (VigilX Cyan #00C8F0) */}
        <motion.div
          animate={{ y: [-4, 4, -4] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
          style={{ position: 'absolute', top: 35, left: 5, transform: 'translateZ(50px)', zIndex: 10 }}
        >
          <div style={{
            background: 'rgba(10, 14, 22, 0.85)', border: '1px solid rgba(0, 200, 240, 0.45)',
            backdropFilter: 'blur(16px)', borderRadius: 20, padding: '8px 18px',
            fontSize: 12, color: '#F8FAFC', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 8,
            boxShadow: '0 8px 24px rgba(0, 200, 240, 0.35)'
          }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#00C8F0', boxShadow: '0 0 10px #00C8F0' }} />
            <BarChart3 size={15} style={{ color: '#00C8F0' }} /> Real-time Analytics
          </div>

          <div style={{
            width: 88, height: 60, borderRadius: 16,
            background: 'linear-gradient(135deg, rgba(8, 28, 48, 0.92), rgba(4, 14, 28, 0.96))',
            border: '1px solid rgba(0, 200, 240, 0.55)',
            boxShadow: '0 0 24px rgba(0, 200, 240, 0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '8px auto 0'
          }}>
            <BarChart3 size={28} style={{ color: '#00C8F0' }} />
          </div>
        </motion.div>

        {/* NODE 2 (Top-Right): Smart Automation (Electric Violet #8B5CF6) */}
        <motion.div
          animate={{ y: [4, -4, 4] }}
          transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut', delay: 0.3 }}
          style={{ position: 'absolute', top: 35, right: 5, transform: 'translateZ(50px)', zIndex: 10 }}
        >
          <div style={{
            background: 'rgba(10, 14, 22, 0.85)', border: '1px solid rgba(139, 92, 246, 0.45)',
            backdropFilter: 'blur(16px)', borderRadius: 20, padding: '8px 18px',
            fontSize: 12, color: '#F8FAFC', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 8,
            boxShadow: '0 8px 24px rgba(139, 92, 246, 0.35)'
          }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#A855F7', boxShadow: '0 0 10px #A855F7' }} />
            <Settings size={15} style={{ color: '#C084FC' }} /> Smart Automation
          </div>

          <div style={{
            width: 88, height: 60, borderRadius: 16,
            background: 'linear-gradient(135deg, rgba(28, 18, 48, 0.92), rgba(14, 8, 28, 0.96))',
            border: '1px solid rgba(139, 92, 246, 0.55)',
            boxShadow: '0 0 24px rgba(139, 92, 246, 0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '8px auto 0'
          }}>
            <Settings size={28} style={{ color: '#A855F7' }} />
          </div>
        </motion.div>

        {/* NODE 3 (Bottom-Left): Graph Intelligence (Emerald #10B981) */}
        <motion.div
          animate={{ y: [-4, 4, -4] }}
          transition={{ duration: 4.2, repeat: Infinity, ease: 'easeInOut', delay: 0.6 }}
          style={{ position: 'absolute', bottom: 25, left: 5, transform: 'translateZ(50px)', zIndex: 10 }}
        >
          <div style={{
            width: 88, height: 60, borderRadius: 16,
            background: 'linear-gradient(135deg, rgba(8, 40, 28, 0.92), rgba(4, 20, 14, 0.96))',
            border: '1px solid rgba(16, 185, 129, 0.55)',
            boxShadow: '0 0 24px rgba(16, 185, 129, 0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 8px'
          }}>
            <PieChart size={28} style={{ color: '#10B981' }} />
          </div>

          <div style={{
            background: 'rgba(10, 14, 22, 0.85)', border: '1px solid rgba(16, 185, 129, 0.45)',
            backdropFilter: 'blur(16px)', borderRadius: 20, padding: '8px 18px',
            fontSize: 12, color: '#F8FAFC', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 8,
            boxShadow: '0 8px 24px rgba(16, 185, 129, 0.35)'
          }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#10B981', boxShadow: '0 0 10px #10B981' }} />
            <PieChart size={15} style={{ color: '#34D399' }} /> Graph Intelligence
          </div>
        </motion.div>

        {/* NODE 4 (Bottom-Right): Air-Gap Security (Sky Blue #38BDF8) */}
        <motion.div
          animate={{ y: [4, -4, 4] }}
          transition={{ duration: 3.8, repeat: Infinity, ease: 'easeInOut', delay: 0.8 }}
          style={{ position: 'absolute', bottom: 25, right: 5, transform: 'translateZ(50px)', zIndex: 10 }}
        >
          <div style={{
            width: 88, height: 60, borderRadius: 16,
            background: 'linear-gradient(135deg, rgba(8, 36, 54, 0.92), rgba(4, 18, 28, 0.96))',
            border: '1px solid rgba(56, 189, 248, 0.55)',
            boxShadow: '0 0 24px rgba(56, 189, 248, 0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 8px'
          }}>
            <ShieldCheck size={28} style={{ color: '#38BDF8' }} />
          </div>

          <div style={{
            background: 'rgba(10, 14, 22, 0.85)', border: '1px solid rgba(56, 189, 248, 0.45)',
            backdropFilter: 'blur(16px)', borderRadius: 20, padding: '8px 18px',
            fontSize: 12, color: '#F8FAFC', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 8,
            boxShadow: '0 8px 24px rgba(56, 189, 248, 0.35)'
          }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#38BDF8', boxShadow: '0 0 10px #38BDF8' }} />
            <ShieldCheck size={15} style={{ color: '#38BDF8' }} /> Air-Gap Security
          </div>
        </motion.div>

      </motion.div>
    </div>
  )
}
