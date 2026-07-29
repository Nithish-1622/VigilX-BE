import { useRef, useEffect, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Float, MeshTransmissionMaterial, Environment } from '@react-three/drei'
import * as THREE from 'three'

function HolographicCore({ mouse }) {
  const outerSphereRef = useRef()
  const innerNeuralRef = useRef()
  const ring1Ref = useRef()
  const ring2Ref = useRef()
  const ring3Ref = useRef()
  const groupRef = useRef()
  const smoothMouse = useRef({ x: 0, y: 0 })

  // Data telemetry nodes along orbital rings
  const ringNodes = useMemo(() => {
    return Array.from({ length: 12 }, (_, i) => {
      const angle = (i / 12) * Math.PI * 2
      return { angle, radius: 1.55, speed: 0.5 + Math.random() * 0.5 }
    })
  }, [])

  useFrame((state, delta) => {
    if (!groupRef.current || !outerSphereRef.current) return

    // Smooth lerp mouse coordinates for 3D parallax tilt
    smoothMouse.current.x += (mouse.current.x - smoothMouse.current.x) * 0.06
    smoothMouse.current.y += (mouse.current.y - smoothMouse.current.y) * 0.06

    // Core sphere rotation
    outerSphereRef.current.rotation.y += delta * 0.2
    outerSphereRef.current.rotation.x += delta * 0.12

    if (innerNeuralRef.current) {
      innerNeuralRef.current.rotation.y -= delta * 0.3
      innerNeuralRef.current.rotation.z += delta * 0.15
    }

    // Orbital Rings Revolution
    if (ring1Ref.current) ring1Ref.current.rotation.z += delta * 0.4
    if (ring2Ref.current) ring2Ref.current.rotation.x -= delta * 0.3
    if (ring3Ref.current) ring3Ref.current.rotation.y += delta * 0.35

    // Mouse Parallax Group Tilt
    groupRef.current.rotation.y = smoothMouse.current.x * 0.35
    groupRef.current.rotation.x = -smoothMouse.current.y * 0.28
  })

  return (
    <group ref={groupRef}>
      <Float speed={2.2} rotationIntensity={0.4} floatIntensity={0.8}>

        {/* 1. Outer Refractive Crystal Geodesic Orb */}
        <mesh ref={outerSphereRef}>
          <icosahedronGeometry args={[1.05, 3]} />
          <MeshTransmissionMaterial
            backside
            backsideThickness={1.2}
            thickness={1.5}
            roughness={0.04}
            transmission={0.95}
            ior={1.5}
            chromaticAberration={0.06}
            anisotropy={0.2}
            color="#00c8f0"
            attenuationColor="#8b5cf6"
            attenuationDistance={0.85}
            clearcoat={1.0}
            clearcoatRoughness={0.02}
          />
        </mesh>

        {/* 2. Inner Glowing Neural Brain Core */}
        <mesh ref={innerNeuralRef}>
          <icosahedronGeometry args={[0.72, 2]} />
          <meshBasicMaterial
            color="#00f0c8"
            wireframe
            transparent
            opacity={0.55}
          />
        </mesh>

        {/* 3. Primary Orbital Data Ring (Cyan) */}
        <group ref={ring1Ref} rotation={[Math.PI / 4, 0, 0]}>
          <mesh>
            <torusGeometry args={[1.55, 0.018, 16, 120]} />
            <meshStandardMaterial
              color="#00c8f0"
              emissive="#00c8f0"
              emissiveIntensity={1.2}
              roughness={0.1}
              metalness={0.8}
            />
          </mesh>

          {/* Telemetry Node Dots on Ring 1 */}
          {ringNodes.slice(0, 4).map((node, idx) => (
            <mesh key={idx} position={[Math.cos(node.angle) * 1.55, Math.sin(node.angle) * 1.55, 0]}>
              <sphereGeometry args={[0.045, 12, 12]} />
              <meshBasicMaterial color="#00f0c8" />
            </mesh>
          ))}
        </group>

        {/* 4. Secondary Orbital Data Ring (Violet) */}
        <group ref={ring2Ref} rotation={[-Math.PI / 6, Math.PI / 3, 0]}>
          <mesh>
            <torusGeometry args={[1.82, 0.016, 16, 120]} />
            <meshStandardMaterial
              color="#8b5cf6"
              emissive="#8b5cf6"
              emissiveIntensity={1.4}
              roughness={0.1}
              metalness={0.8}
            />
          </mesh>

          {/* Telemetry Node Dots on Ring 2 */}
          {ringNodes.slice(4, 8).map((node, idx) => (
            <mesh key={idx} position={[Math.cos(node.angle + 1) * 1.82, Math.sin(node.angle + 1) * 1.82, 0]}>
              <sphereGeometry args={[0.04, 12, 12]} />
              <meshBasicMaterial color="#a78bfa" />
            </mesh>
          ))}
        </group>

        {/* 5. Outer Equatorial Perimeter Ring (Teal) */}
        <group ref={ring3Ref} rotation={[0, 0, Math.PI / 5]}>
          <mesh>
            <torusGeometry args={[2.08, 0.012, 16, 120]} />
            <meshBasicMaterial color="#00f0c8" transparent opacity={0.35} />
          </mesh>
        </group>

      </Float>
    </group>
  )
}

export default function CyberKnotScene({ style }) {
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
    <div style={{ position: 'relative', width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', ...style }}>
      
      {/* Background Radial Glow Aura */}
      <div style={{
        position: 'absolute', top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)', width: '85%', height: '85%',
        background: 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.26) 0%, rgba(0, 200, 240, 0.18) 45%, transparent 75%)',
        filter: 'blur(45px)', pointerEvents: 'none', zIndex: 0
      }} />

      <Canvas
        camera={{ position: [0, 0, 4.4], fov: 42 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        style={{ position: 'relative', zIndex: 1, background: 'transparent', width: '100%', height: '100%' }}
      >
        {/* Real-World Studio HDRI Environment Lighting */}
        <Environment preset="city" />

        {/* Accent Lights */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} color="#00c8f0" intensity={2.8} />
        <pointLight position={[-8, -8, -4]} color="#8b5cf6" intensity={3.5} />
        <pointLight position={[4, -3, 5]} color="#00f0c8" intensity={2.2} />

        <HolographicCore mouse={mouse} />
      </Canvas>
    </div>
  )
}
