import { useRef, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Float, MeshTransmissionMaterial, Environment } from '@react-three/drei'
import * as THREE from 'three'

function PhotorealisticPurpleRibbon({ mouse }) {
  const outerMeshRef = useRef()
  const innerMeshRef = useRef()
  const groupRef = useRef()
  const smoothMouse = useRef({ x: 0, y: 0 })

  useFrame((state, delta) => {
    if (!groupRef.current || !outerMeshRef.current) return

    // Smooth lerp mouse coordinates for 3D parallax tilt
    smoothMouse.current.x += (mouse.current.x - smoothMouse.current.x) * 0.06
    smoothMouse.current.y += (mouse.current.y - smoothMouse.current.y) * 0.06

    // Smooth liquid rotation
    outerMeshRef.current.rotation.x += delta * 0.22
    outerMeshRef.current.rotation.y += delta * 0.32

    if (innerMeshRef.current) {
      innerMeshRef.current.rotation.x -= delta * 0.16
      innerMeshRef.current.rotation.y -= delta * 0.24
    }

    // Cursor parallax tilt
    groupRef.current.rotation.y = smoothMouse.current.x * 0.38
    groupRef.current.rotation.x = -smoothMouse.current.y * 0.32
  })

  return (
    <group ref={groupRef}>
      <Float speed={2.5} rotationIntensity={0.5} floatIntensity={0.9}>
        
        {/* Outer Photorealistic Purple Glass Mobius Ribbon */}
        <mesh ref={outerMeshRef}>
          <torusKnotGeometry args={[1.25, 0.44, 240, 36, 2, 3]} />
          <MeshTransmissionMaterial
            backside
            backsideThickness={1.4}
            thickness={1.8}
            roughness={0.03}
            transmission={0.94}
            ior={1.52}
            chromaticAberration={0.09}
            anisotropy={0.3}
            distortion={0.15}
            distortionScale={0.3}
            temporalDistortion={0.1}
            color="#8b5cf6"
            attenuationColor="#d946ef"
            attenuationDistance={0.75}
            clearcoat={1.0}
            clearcoatRoughness={0.02}
          />
        </mesh>

        {/* Inner Volumetric Metallic Core */}
        <mesh ref={innerMeshRef} scale={[0.86, 0.86, 0.86]}>
          <torusKnotGeometry args={[1.25, 0.3, 160, 24, 2, 3]} />
          <meshStandardMaterial
            color="#090514"
            emissive="#8b5cf6"
            emissiveIntensity={0.65}
            metalness={0.95}
            roughness={0.08}
          />
        </mesh>

      </Float>
    </group>
  )
}

export default function GlassRibbonScene({ style }) {
  const mouse = useRef({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e) => {
      mouse.current.x = (e.clientX / window.innerWidth - 0.5) * 2.0
      mouse.current.y = -(e.clientY / window.innerHeight - 0.5) * 2.0
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'visible', ...style }}>
      {/* Deep Photorealistic Purple Radial Glow Aura */}
      <div style={{
        position: 'absolute', top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)', width: '92%', height: '92%',
        background: 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.45) 0%, rgba(217, 70, 239, 0.22) 42%, transparent 78%)',
        filter: 'blur(55px)', pointerEvents: 'none', zIndex: 0
      }} />

      <Canvas
        camera={{ position: [0, 0, 3.9], fov: 46 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        style={{ position: 'relative', zIndex: 1, background: 'transparent', width: '100%', height: 580 }}
      >
        {/* Real-World Studio Environment HDRI Lighting */}
        <Environment preset="city" />

        {/* Dynamic Studio Spot & Point Lights */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} color="#ffffff" intensity={3.2} />
        <pointLight position={[-10, -10, -5]} color="#8b5cf6" intensity={4.5} />
        <pointLight position={[5, -5, 5]} color="#d946ef" intensity={3.5} />

        <PhotorealisticPurpleRibbon mouse={mouse} />
      </Canvas>
    </div>
  )
}
