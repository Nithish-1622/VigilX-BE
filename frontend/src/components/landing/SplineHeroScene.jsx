import { useState } from 'react'
import { Loader2, RefreshCw } from 'lucide-react'
import Spline from '@splinetool/react-spline'

export default function SplineHeroScene({ style }) {
  const [loaded, setLoaded] = useState(false)
  const [hasError, setHasError] = useState(false)

  // Syngri 3D Photorealistic Purple Glass Mobius Infinity Ribbon Scene
  const splineSceneUrl = 'https://prod.spline.design/6Wnt13KcwWvh2yRJ/scene.splinecode'

  function onLoad() {
    setLoaded(true)
  }

  function onError() {
    setHasError(true)
  }

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: 580,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'transparent',
        overflow: 'visible',
        ...style
      }}
    >
      {/* Deep Purple/Violet Radial Glow Aura behind the 3D model */}
      <div
        style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '90%', height: '90%',
          background: 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.42) 0%, rgba(0, 200, 240, 0.18) 45%, transparent 75%)',
          filter: 'blur(60px)', pointerEvents: 'none', zIndex: 0
        }}
      />

      {/* Loading Fallback Spinner */}
      {!loaded && !hasError && (
        <div
          style={{
            position: 'absolute', inset: 0, zIndex: 10,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12,
            background: 'transparent'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 18px', borderRadius: 20, background: 'rgba(10, 14, 22, 0.8)', border: '1px solid rgba(0, 200, 240, 0.25)', backdropFilter: 'blur(10px)' }}>
            <Loader2 size={16} style={{ color: '#00C8F0', animation: 'spin 1.2s linear infinite' }} />
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#00C8F0', letterSpacing: '0.08em' }}>
              LOADING 3D GLASS SCULPTURE...
            </span>
          </div>
        </div>
      )}

      {/* Error Fallback */}
      {hasError ? (
        <div style={{ padding: 24, textAlign: 'center', zIndex: 10 }}>
          <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#EF4444', marginBottom: 8 }}>
            UNABLE TO LOAD SPLINE 3D STREAM
          </div>
          <button
            onClick={() => setHasError(false)}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 20,
              fontSize: 10, fontFamily: 'JetBrains Mono, monospace', color: '#00C8F0', background: 'rgba(0, 200, 240, 0.1)',
              border: '1px solid rgba(0, 200, 240, 0.3)', cursor: 'pointer'
            }}
          >
            <RefreshCw size={11} /> RETRY CONNECTION
          </button>
        </div>
      ) : (
        /* Seamless Floating 3D Spline Canvas */
        <div style={{ position: 'relative', width: '100%', height: '100%', zIndex: 1 }}>
          <Spline
            scene={splineSceneUrl}
            onLoad={onLoad}
            onError={onError}
            style={{ width: '100%', height: '100%' }}
          />
        </div>
      )}
    </div>
  )
}
