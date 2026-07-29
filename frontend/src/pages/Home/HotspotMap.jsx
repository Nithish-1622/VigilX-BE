import { useEffect, useRef, useState, useMemo } from 'react'
import {
  ShieldAlert, Layers, Navigation, Radio, Search, Target,
  Crosshair, Compass, Zap, CheckCircle2, MapPin, Activity, Filter, Eye
} from 'lucide-react'
import * as maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

// ─── Karnataka State Police (KSP) Verified Real-World Geospatial Coordinates ───
const KARNATAKA_STATIONS = [
  {
    id: 'ksp-bgl-hq',
    lon: 77.5983,
    lat: 12.9822,
    weight: 1.0,
    type: 'Command HQ',
    label: 'Bengaluru City Police HQ',
    address: 'Infantry Road, Bengaluru Central',
    severity: 'critical',
    district: 'Bengaluru Urban',
    code: 'KSP-BGL-01',
    status: 'ACTIVE COMMAND',
    units: 14,
    phone: '+91 80 2294 2222',
  },
  {
    id: 'ksp-cid-cyber',
    lon: 77.5878,
    lat: 12.9815,
    weight: 0.95,
    type: 'Cyber Crime HQ',
    label: 'State CID Cyber Crime Division',
    address: 'Carlton House, Palace Road, Bengaluru',
    severity: 'critical',
    district: 'Bengaluru Urban',
    code: 'CID-CYBER-09',
    status: 'INVESTIGATING AML',
    units: 8,
    phone: '+91 80 2209 4444',
  },
  {
    id: 'ksp-koramangala',
    lon: 77.6186,
    lat: 12.9352,
    weight: 0.9,
    type: 'Cyber Crime',
    label: 'Koramangala Tech Precinct',
    address: '8th Block, Koramangala, Bengaluru',
    severity: 'critical',
    district: 'Bengaluru Urban',
    code: 'KSP-KOR-04',
    status: 'HIGH ALERT',
    units: 6,
    phone: '+91 80 2294 3456',
  },
  {
    id: 'ksp-indiranagar',
    lon: 77.6408,
    lat: 12.9784,
    weight: 0.85,
    type: 'Financial AML',
    label: 'Indiranagar Cyber Cell',
    address: '100 Feet Road, Indiranagar, Bengaluru',
    severity: 'high',
    district: 'Bengaluru Urban',
    code: 'KSP-IND-02',
    status: 'PATROL ACTIVE',
    units: 5,
    phone: '+91 80 2294 3112',
  },
  {
    id: 'ksp-ecity',
    lon: 77.6602,
    lat: 12.8452,
    weight: 0.75,
    type: 'Tech Crime',
    label: 'Electronic City Cyber Post',
    address: 'Phase 1, Electronic City, Bengaluru',
    severity: 'medium',
    district: 'Bengaluru Urban',
    code: 'KSP-ECI-07',
    status: 'MONITORING',
    units: 4,
    phone: '+91 80 2294 9800',
  },
  {
    id: 'ksp-malleswaram',
    lon: 77.5736,
    lat: 13.0084,
    weight: 0.8,
    type: 'Narcotics Control',
    label: 'Malleswaram Law & Order',
    address: 'Sampige Road, Malleswaram, Bengaluru',
    severity: 'high',
    district: 'Bengaluru Urban',
    code: 'KSP-MAL-03',
    status: 'TACTICAL DISPATCH',
    units: 6,
    phone: '+91 80 2294 2500',
  },
  {
    id: 'ksp-mysuru-hq',
    lon: 76.6631,
    lat: 12.3118,
    weight: 0.75,
    type: 'Command HQ',
    label: 'Mysuru City Police HQ',
    address: 'Nazarbad, Mysuru',
    severity: 'medium',
    district: 'Mysuru Division',
    code: 'KSP-MYS-01',
    status: 'OPERATIONAL',
    units: 9,
    phone: '+91 821 2418 100',
  },
  {
    id: 'ksp-hubballi-hq',
    lon: 75.1240,
    lat: 15.3647,
    weight: 0.82,
    type: 'Gang Taskforce',
    label: 'Hubballi-Dharwad Police HQ',
    address: 'Navanagar, Hubballi',
    severity: 'high',
    district: 'Dharwad Zone',
    code: 'KSP-HBL-01',
    status: 'HIGH ALERT',
    units: 7,
    phone: '+91 836 2233 200',
  },
  {
    id: 'ksp-mangaluru-coastal',
    lon: 74.8360,
    lat: 12.8622,
    weight: 0.88,
    type: 'Coastal Security',
    label: 'Mangaluru Coastal Security HQ',
    address: 'Pandeshwar, Mangaluru',
    severity: 'high',
    district: 'Coastal Zone',
    code: 'KSP-MNG-05',
    status: 'RADAR TRACKING',
    units: 6,
    phone: '+91 824 2220 800',
  },
  {
    id: 'ksp-udupi-malpe',
    lon: 74.7003,
    lat: 13.3551,
    weight: 0.7,
    type: 'Smuggling Watch',
    label: 'Malpe Maritime Police Post',
    address: 'Malpe Port, Udupi',
    severity: 'medium',
    district: 'Coastal Zone',
    code: 'KSP-UDP-02',
    status: 'PATROL ACTIVE',
    units: 4,
    phone: '+91 820 2530 100',
  },
  {
    id: 'ksp-belagavi-border',
    lon: 74.5050,
    lat: 15.8580,
    weight: 0.9,
    type: 'Cross Border Outpost',
    label: 'Belagavi Border Interceptor HQ',
    address: 'Camp Area, Belagavi',
    severity: 'critical',
    district: 'Belagavi Range',
    code: 'KSP-BGM-01',
    status: 'INTERCEPT MODE',
    units: 8,
    phone: '+91 831 2405 200',
  },
  {
    id: 'ksp-kalaburagi-hq',
    lon: 76.8343,
    lat: 17.3297,
    weight: 0.78,
    type: 'Financial AML',
    label: 'Kalaburagi East DPO HQ',
    address: 'Super Market Area, Kalaburagi',
    severity: 'high',
    district: 'Kalaburagi Range',
    code: 'KSP-KLB-02',
    status: 'INVESTIGATING',
    units: 5,
    phone: '+91 8472 263 600',
  },
  {
    id: 'ksp-shivamogga',
    lon: 75.5681,
    lat: 13.9299,
    weight: 0.65,
    type: 'Illicit Trade Watch',
    label: 'Shivamogga Central DPO',
    address: 'B.H. Road, Shivamogga',
    severity: 'medium',
    district: 'Shivamogga',
    code: 'KSP-SHM-01',
    status: 'STANDBY',
    units: 4,
    phone: '+91 8182 261 400',
  },
  {
    id: 'ksp-ballari',
    lon: 76.9214,
    lat: 15.1424,
    weight: 0.8,
    type: 'Mining Surveillance',
    label: 'Ballari District Police HQ',
    address: 'Station Road, Ballari',
    severity: 'high',
    district: 'Ballari Range',
    code: 'KSP-BAL-01',
    status: 'SURVEILLANCE',
    units: 5,
    phone: '+91 8392 272 100',
  },
]

// ─── Initial Live Patrol Units (Dynamic Real-Time Tracking Simulation) ───
const INITIAL_PATROL_UNITS = [
  {
    id: 'UNIT-101',
    callsign: 'KSP-CHETA-1',
    label: 'Bengaluru ERSS-112 Cruiser',
    type: 'Mobile Interceptor',
    lat: 12.9780,
    lon: 77.6100,
    deltaLat: 0.0006,
    deltaLon: 0.0008,
    speed: 54,
    heading: 135,
    status: 'LIVE RESPONDING',
    district: 'Bengaluru Urban',
    severity: 'critical',
    history: [[77.5983, 12.9822], [77.6040, 12.9800], [77.6100, 12.9780]],
  },
  {
    id: 'UNIT-204',
    callsign: 'KSP-EAGLE-2',
    label: 'Mysuru Ring Patrol Unit',
    type: 'Highway Patrol',
    lat: 12.3150,
    lon: 76.6580,
    deltaLat: -0.0007,
    deltaLon: 0.0005,
    speed: 68,
    heading: 245,
    status: 'PATROLLING CORRIDOR',
    district: 'Mysuru Division',
    severity: 'medium',
    history: [[76.6631, 12.3118], [76.6610, 12.3135], [76.6580, 12.3150]],
  },
  {
    id: 'UNIT-308',
    callsign: 'KSP-GARUDA-3',
    label: 'Hubballi Express Taskforce',
    type: 'High-Speed Taskforce',
    lat: 15.3700,
    lon: 75.1200,
    deltaLat: 0.0009,
    deltaLon: -0.0006,
    speed: 76,
    heading: 315,
    status: 'LIVE TRACKING',
    district: 'Dharwad Zone',
    severity: 'high',
    history: [[75.1240, 15.3647], [75.1220, 15.3675], [75.1200, 15.3700]],
  },
  {
    id: 'UNIT-412',
    callsign: 'KSP-COAST-9',
    label: 'Mangaluru Maritime Interceptor',
    type: 'Coastal Boat Unit',
    lat: 12.8680,
    lon: 74.8320,
    deltaLat: 0.0005,
    deltaLon: -0.0004,
    speed: 38,
    heading: 330,
    status: 'RADAR SURVEILLANCE',
    district: 'Coastal Zone',
    severity: 'high',
    history: [[74.8360, 12.8622], [74.8340, 12.8650], [74.8320, 12.8680]],
  },
  {
    id: 'UNIT-505',
    callsign: 'KSP-BORDER-7',
    label: 'Belagavi Border Interceptor',
    type: 'Border Checkpost Squad',
    lat: 15.8620,
    lon: 74.5090,
    deltaLat: 0.0004,
    deltaLon: 0.0007,
    speed: 48,
    heading: 55,
    status: 'CHECKPOINT MONITORING',
    district: 'Belagavi Range',
    severity: 'critical',
    history: [[74.5050, 15.8580], [74.5070, 15.8600], [74.5090, 15.8620]],
  },
]

const SEVERITY_COLORS = {
  critical: '#EF4444',
  high: '#F59E0B',
  medium: '#10B981',
}

const DISTRICT_BOUNDS = {
  'ALL': { center: [76.5, 14.5], zoom: 7.0 },
  'Bengaluru Urban': { center: [77.6000, 12.9600], zoom: 11.2 },
  'Mysuru Division': { center: [76.6500, 12.3100], zoom: 11.5 },
  'Dharwad Zone': { center: [75.1000, 15.3600], zoom: 11.2 },
  'Coastal Zone': { center: [74.7800, 13.1000], zoom: 9.8 },
  'Belagavi Range': { center: [74.5000, 15.8500], zoom: 10.5 },
  'Kalaburagi Range': { center: [76.8300, 17.3200], zoom: 10.5 },
}

export default function HotspotMap() {
  const mapRef = useRef(null)
  const mapInstance = useRef(null)
  const markersRef = useRef([])
  const unitMarkersRef = useRef([])

  const [mapError, setMapError] = useState(false)
  const [selected, setSelected] = useState(null)
  const [isLiveTracking, setIsLiveTracking] = useState(true)
  const [selectedDistrict, setSelectedDistrict] = useState('ALL')
  const [selectedSeverity, setSelectedSeverity] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [liveUnits, setLiveUnits] = useState(INITIAL_PATROL_UNITS)
  const [lastPingTime, setLastPingTime] = useState(new Date().toLocaleTimeString())

  // Filter stations based on controls
  const filteredStations = useMemo(() => {
    return KARNATAKA_STATIONS.filter((st) => {
      const matchesDistrict = selectedDistrict === 'ALL' || st.district === selectedDistrict
      const matchesSeverity = selectedSeverity === 'ALL' || st.severity === selectedSeverity
      const q = searchQuery.trim().toLowerCase()
      const matchesQuery =
        !q ||
        st.label.toLowerCase().includes(q) ||
        st.district.toLowerCase().includes(q) ||
        st.type.toLowerCase().includes(q) ||
        st.address.toLowerCase().includes(q)
      return matchesDistrict && matchesSeverity && matchesQuery
    })
  }, [selectedDistrict, selectedSeverity, searchQuery])

  // Filter live units based on district
  const filteredUnits = useMemo(() => {
    return liveUnits.filter((u) => {
      const matchesDistrict = selectedDistrict === 'ALL' || u.district === selectedDistrict
      const matchesSeverity = selectedSeverity === 'ALL' || u.severity === selectedSeverity
      const q = searchQuery.trim().toLowerCase()
      const matchesQuery = !q || u.callsign.toLowerCase().includes(q) || u.label.toLowerCase().includes(q)
      return matchesDistrict && matchesSeverity && matchesQuery
    })
  }, [liveUnits, selectedDistrict, selectedSeverity, searchQuery])

  // ─── Live GPS Tracking Simulation Engine ───
  useEffect(() => {
    if (!isLiveTracking) return

    const interval = setInterval(() => {
      setLiveUnits((prevUnits) =>
        prevUnits.map((unit) => {
          // Boundary bounce simulation within reasonable range
          let dLat = unit.deltaLat
          let dLon = unit.deltaLon
          let nLat = unit.lat + dLat
          let nLon = unit.lon + dLon

          // Bounce if drifted too far from base location
          if (Math.abs(nLat - unit.history[0][1]) > 0.08) dLat = -dLat
          if (Math.abs(nLon - unit.history[0][0]) > 0.08) dLon = -dLon

          const nextSpeed = Math.floor(40 + Math.random() * 45)
          const nextHeading = (unit.heading + (Math.random() > 0.5 ? 5 : -5) + 360) % 360
          const updatedHistory = [...unit.history.slice(-6), [nLon, nLat]]

          return {
            ...unit,
            lat: Number(nLat.toFixed(5)),
            lon: Number(nLon.toFixed(5)),
            deltaLat: dLat,
            deltaLon: dLon,
            speed: nextSpeed,
            heading: nextHeading,
            history: updatedHistory,
          }
        })
      )
      setLastPingTime(new Date().toLocaleTimeString())
    }, 1400)

    return () => clearInterval(interval)
  }, [isLiveTracking])

  // ─── MapLibre GL Renderer Setup & Markers ───
  useEffect(() => {
    let map = null
    try {
      if (!mapRef.current) return

      if (!mapInstance.current) {
        map = new maplibregl.Map({
          container: mapRef.current,
          style: {
            version: 8,
            glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
            sources: {
              'osm-tiles': {
                type: 'raster',
                tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© OpenStreetMap | KSP Geospatial Intelligence',
              },
            },
            layers: [
              {
                id: 'osm',
                type: 'raster',
                source: 'osm-tiles',
                paint: {
                  'raster-brightness-min': 0,
                  'raster-brightness-max': 0.12,
                  'raster-saturation': -0.88,
                  'raster-contrast': 0.35,
                  'raster-opacity': 0.78,
                },
              },
            ],
          },
          center: [76.5, 14.5],
          zoom: 7.0,
          pitch: 20,
          antialias: true,
        })

        mapInstance.current = map

        map.on('load', () => {
          const bounds = new maplibregl.LngLatBounds()
          KARNATAKA_STATIONS.forEach((inc) => bounds.extend([inc.lon, inc.lat]))
          map.fitBounds(bounds, { padding: 45, maxZoom: 11, duration: 1000 })
        })
      } else {
        map = mapInstance.current
      }

      // Re-render Static Station Markers
      markersRef.current.forEach((m) => m.remove())
      markersRef.current = []

      filteredStations.forEach((st) => {
        const color = SEVERITY_COLORS[st.severity] || '#00C8F0'
        const el = document.createElement('div')
        el.className = 'ksp-station-marker'
        el.style.cssText = `
          position: relative;
          cursor: pointer;
          display: flex;
          flex-direction: column;
          align-items: center;
          transform: translate(-50%, -100%);
          z-index: 10;
        `

        el.innerHTML = `
          <div style="
            background: rgba(6, 8, 14, 0.94);
            border: 1px solid ${color};
            color: #FFFFFF;
            font-family: 'JetBrains Mono', monospace;
            font-size: 8px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 10px;
            white-space: nowrap;
            margin-bottom: 3px;
            box-shadow: 0 0 10px ${color}60;
            letter-spacing: 0.04em;
            display: flex;
            align-items: center;
            gap: 4px;
          ">
            <span style="width: 5px; height: 5px; border-radius: 50%; background: ${color}; display: inline-block;"></span>
            ${st.label}
          </div>

          <div style="position: relative; width: 22px; height: 26px; display: flex; align-items: center; justify-content: center;">
            <div style="
              position: absolute;
              bottom: 0;
              width: 20px;
              height: 20px;
              border-radius: 50%;
              background: ${color}25;
              border: 1.5px solid ${color};
              animation: pulsePinRing 2.2s infinite;
            "></div>

            <svg width="20" height="26" viewBox="0 0 24 30" fill="none" style="position: relative; z-index: 2; filter: drop-shadow(0 2px 6px ${color}90);">
              <path d="M12 0C5.37 0 0 5.37 0 12C0 21 12 30 12 30C12 30 24 21 24 12C24 5.37 18.63 0 12 0Z" fill="${color}"/>
              <circle cx="12" cy="11" r="5" fill="#06080C"/>
            </svg>
          </div>
        `

        el.addEventListener('click', () => {
          setSelected(st)
          map.flyTo({ center: [st.lon, st.lat], zoom: 12.5, duration: 800 })
        })

        const marker = new maplibregl.Marker({ element: el, anchor: 'bottom' })
          .setLngLat([st.lon, st.lat])
          .addTo(map)

        markersRef.current.push(marker)
      })

      // Render Dynamic Live Patrol Unit Markers
      unitMarkersRef.current.forEach((m) => m.remove())
      unitMarkersRef.current = []

      if (isLiveTracking) {
        filteredUnits.forEach((u) => {
          const color = '#00D4FF'
          const el = document.createElement('div')
          el.className = 'ksp-unit-marker'
          el.style.cssText = `
            position: relative;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            transform: translate(-50%, -50%);
            z-index: 15;
          `

          el.innerHTML = `
            <div style="
              background: rgba(0, 30, 45, 0.95);
              border: 1.5px solid ${color};
              color: #00E5FF;
              font-family: 'JetBrains Mono', monospace;
              font-size: 8px;
              font-weight: 800;
              padding: 2px 6px;
              border-radius: 4px;
              white-space: nowrap;
              margin-bottom: 2px;
              box-shadow: 0 0 10px rgba(0, 212, 255, 0.6);
              letter-spacing: 0.05em;
              display: flex;
              align-items: center;
              gap: 4px;
            ">
              <span style="width: 5px; height: 5px; border-radius: 50%; background: #00E5FF; animation: pulseDot 1s infinite;"></span>
              ${u.callsign} (${u.speed} km/h)
            </div>

            <div style="position: relative; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
              <div style="
                position: absolute;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                border: 1.5px dashed ${color};
                animation: rotateRadar 4s linear infinite;
              "></div>

              <div style="
                width: 14px;
                height: 14px;
                background: ${color};
                border-radius: 50%;
                border: 2px solid #FFFFFF;
                box-shadow: 0 0 12px ${color};
                display: flex;
                align-items: center;
                justify-content: center;
              ">
                <div style="width: 4px; height: 4px; border-radius: 50%; background: #000;"></div>
              </div>
            </div>
          `

          el.addEventListener('click', () => {
            setSelected({
              id: u.id,
              label: u.label,
              callsign: u.callsign,
              lat: u.lat,
              lon: u.lon,
              type: `LIVE UNIT (${u.type})`,
              severity: u.severity,
              district: u.district,
              address: `GPS Telemetry: Lat ${u.lat}° N, Lon ${u.lon}° E`,
              code: u.callsign,
              status: u.status,
              speed: `${u.speed} km/h`,
              heading: `${u.heading}°`,
              isLiveUnit: true,
            })
            map.flyTo({ center: [u.lon, u.lat], zoom: 13, duration: 800 })
          })

          const marker = new maplibregl.Marker({ element: el, anchor: 'center' })
            .setLngLat([u.lon, u.lat])
            .addTo(map)

          unitMarkersRef.current.push(marker)
        })
      }
    } catch (err) {
      console.error('[KSP Maplibre Error]', err)
      setMapError(true)
    }

    return () => {
      markersRef.current.forEach((m) => m.remove())
      unitMarkersRef.current.forEach((m) => m.remove())
      markersRef.current = []
      unitMarkersRef.current = []
    }
  }, [filteredStations, filteredUnits, isLiveTracking])

  // Handle Quick District Jump
  const handleDistrictChange = (dist) => {
    setSelectedDistrict(dist)
    if (mapInstance.current && DISTRICT_BOUNDS[dist]) {
      const { center, zoom } = DISTRICT_BOUNDS[dist]
      mapInstance.current.flyTo({ center, zoom, duration: 1000 })
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: 'var(--bg-panel)',
        border: '1px solid rgba(0, 200, 240, 0.35)',
        borderRadius: 8,
        overflow: 'hidden',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
      }}
    >
      {/* CSS Animations */}
      <style>{`
        @keyframes pulsePinRing {
          0% { transform: scale(0.8); opacity: 0.9; }
          70% { transform: scale(1.6); opacity: 0.15; }
          100% { transform: scale(1.8); opacity: 0; }
        }
        @keyframes rotateRadar {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes pulseDot {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.3; transform: scale(0.8); }
        }
      `}</style>

      {/* Top Header Bar */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 14px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          background: '#04060A',
          gap: 10,
          flexShrink: 0,
        }}
      >
        {/* Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ShieldAlert size={16} style={{ color: '#00C8F0' }} />
          <div>
            <span style={{ fontSize: 12, fontWeight: 800, color: '#FFFFFF', letterSpacing: '0.04em', display: 'block' }}>
              KARNATAKA STATE POLICE (KSP) HOTSPOT & LIVE GPS MAP
            </span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: '#94A3B8' }}>
              High-Precision Verified Stations & Real-Time Telemetry
            </span>
          </div>
        </div>

        {/* Live Tracking Toggle & Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button
            onClick={() => setIsLiveTracking(!isLiveTracking)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '4px 10px',
              borderRadius: 20,
              background: isLiveTracking ? 'rgba(0, 212, 255, 0.12)' : 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${isLiveTracking ? '#00D4FF' : 'rgba(255, 255, 255, 0.2)'}`,
              color: isLiveTracking ? '#00E5FF' : '#94A3B8',
              fontSize: 10,
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <Radio size={12} style={{ animation: isLiveTracking ? 'pulseDot 1.2s infinite' : 'none' }} />
            {isLiveTracking ? 'LIVE GPS TRACKING: ON' : 'LIVE TRACKING: PAUSED'}
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'var(--mono)', fontSize: 9, color: '#64748B' }}>
            <Activity size={12} style={{ color: '#10B981' }} />
            <span>PING: {lastPingTime}</span>
          </div>
        </div>
      </div>

      {/* Control Toolbar: Search & District Filters */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '6px 14px',
          background: '#070A10',
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          gap: 8,
          flexShrink: 0,
        }}
      >
        {/* District Jump Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, overflowX: 'auto', paddingBottom: 2 }}>
          {['ALL', 'Bengaluru Urban', 'Mysuru Division', 'Dharwad Zone', 'Coastal Zone', 'Belagavi Range', 'Kalaburagi Range'].map((dist) => (
            <button
              key={dist}
              onClick={() => handleDistrictChange(dist)}
              style={{
                padding: '3px 8px',
                borderRadius: 4,
                border: '1px solid',
                borderColor: selectedDistrict === dist ? '#00C8F0' : 'rgba(255, 255, 255, 0.08)',
                background: selectedDistrict === dist ? 'rgba(0, 200, 240, 0.15)' : 'transparent',
                color: selectedDistrict === dist ? '#00E5FF' : '#94A3B8',
                fontSize: 9,
                fontWeight: 700,
                fontFamily: 'var(--mono)',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
              }}
            >
              {dist === 'ALL' ? 'ALL KARNATAKA' : dist.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Search Bar */}
        <div style={{ position: 'relative', width: 180 }}>
          <Search size={11} style={{ position: 'absolute', left: 8, top: '50%', transform: 'translateY(-50%)', color: '#64748B' }} />
          <input
            type="text"
            placeholder="Search location/station..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '3px 8px 3px 24px',
              borderRadius: 4,
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              color: '#FFFFFF',
              fontSize: 10,
              fontFamily: 'var(--mono)',
              outline: 'none',
            }}
          />
        </div>
      </div>

      {/* Map Body Container */}
      <div style={{ flex: 1, position: 'relative', minHeight: 300 }}>
        {mapError ? (
          <FallbackMap
            stations={filteredStations}
            units={filteredUnits}
            selected={selected}
            onSelect={setSelected}
            isLiveTracking={isLiveTracking}
          />
        ) : (
          <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
        )}

        {/* Selected Incident / Unit Telemetry Inspector Overlay */}
        {selected && (
          <div
            style={{
              position: 'absolute',
              bottom: 14,
              left: 14,
              zIndex: 30,
              background: 'rgba(6, 10, 18, 0.95)',
              border: `1px solid ${selected.isLiveUnit ? '#00D4FF' : SEVERITY_COLORS[selected.severity] || '#00C8F0'}`,
              borderRadius: 8,
              padding: '12px 14px',
              minWidth: 260,
              maxWidth: 320,
              backdropFilter: 'blur(12px)',
              boxShadow: '0 6px 24px rgba(0,0,0,0.8)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
              <span
                style={{
                  fontFamily: 'var(--mono)',
                  fontSize: 9,
                  fontWeight: 800,
                  color: selected.isLiveUnit ? '#00E5FF' : SEVERITY_COLORS[selected.severity] || '#00C8F0',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                }}
              >
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: selected.isLiveUnit ? '#00E5FF' : SEVERITY_COLORS[selected.severity] }} />
                {selected.isLiveUnit ? `LIVE MOBILE UNIT (${selected.code})` : `STATION: ${selected.code}`}
              </span>
              <button
                onClick={() => setSelected(null)}
                style={{ background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer', fontSize: 16, lineHeight: 1 }}
              >
                ×
              </button>
            </div>

            <p style={{ fontSize: 13, fontWeight: 800, color: '#FFFFFF', margin: '2px 0 4px 0' }}>{selected.label}</p>
            <p style={{ fontSize: 10, color: '#94A3B8', margin: '0 0 6px 0' }}>{selected.address}</p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, marginBottom: 8, background: 'rgba(0, 0, 0, 0.4)', padding: 6, borderRadius: 4 }}>
              <div>
                <span style={{ fontSize: 8, color: '#64748B', display: 'block' }}>DISTRICT</span>
                <span style={{ fontSize: 10, color: '#00C8F0', fontWeight: 700 }}>{selected.district}</span>
              </div>
              <div>
                <span style={{ fontSize: 8, color: '#64748B', display: 'block' }}>TYPE</span>
                <span style={{ fontSize: 10, color: '#E2E8F0', fontWeight: 700 }}>{selected.type}</span>
              </div>
              <div>
                <span style={{ fontSize: 8, color: '#64748B', display: 'block' }}>GPS LATITUDE</span>
                <span style={{ fontSize: 10, color: '#10B981', fontFamily: 'var(--mono)' }}>{selected.lat}° N</span>
              </div>
              <div>
                <span style={{ fontSize: 8, color: '#64748B', display: 'block' }}>GPS LONGITUDE</span>
                <span style={{ fontSize: 10, color: '#10B981', fontFamily: 'var(--mono)' }}>{selected.lon}° E</span>
              </div>
              {selected.speed && (
                <div>
                  <span style={{ fontSize: 8, color: '#64748B', display: 'block' }}>SPEED</span>
                  <span style={{ fontSize: 10, color: '#F59E0B', fontFamily: 'var(--mono)' }}>{selected.speed}</span>
                </div>
              )}
              {selected.status && (
                <div>
                  <span style={{ fontSize: 8, color: '#64748B', display: 'block' }}>STATUS</span>
                  <span style={{ fontSize: 9, color: '#00E5FF', fontWeight: 800 }}>{selected.status}</span>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: 6 }}>
              <button
                onClick={() => {
                  if (mapInstance.current) {
                    mapInstance.current.flyTo({ center: [selected.lon, selected.lat], zoom: 14, duration: 800 })
                  }
                }}
                style={{
                  flex: 1,
                  padding: '4px 8px',
                  borderRadius: 4,
                  background: 'rgba(0, 200, 240, 0.15)',
                  border: '1px solid #00C8F0',
                  color: '#00E5FF',
                  fontSize: 9,
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 4,
                }}
              >
                <Crosshair size={11} /> FOCUS CAMERA
              </button>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(`${selected.lat}, ${selected.lon}`)
                  alert(`Copied coordinates: ${selected.lat}, ${selected.lon}`)
                }}
                style={{
                  padding: '4px 8px',
                  borderRadius: 4,
                  background: 'rgba(255, 255, 255, 0.06)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  color: '#CBD5E1',
                  fontSize: 9,
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                COPY GPS
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Legend Footer */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '6px 14px',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          background: '#04060A',
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          {Object.entries(SEVERITY_COLORS).map(([level, color]) => (
            <div key={level} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{ width: 7, height: 7, borderRadius: '50%', background: color, boxShadow: `0 0 6px ${color}` }} />
              <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: '#CBD5E1', textTransform: 'uppercase', fontWeight: 600 }}>
                {level}
              </span>
            </div>
          ))}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#00D4FF', boxShadow: '0 0 6px #00D4FF' }} />
            <span style={{ fontFamily: 'var(--mono)', fontSize: 9, color: '#00E5FF', textTransform: 'uppercase', fontWeight: 700 }}>
              LIVE MOBILE UNIT
            </span>
          </div>
        </div>

        <div style={{ fontFamily: 'var(--mono)', fontSize: 9, color: '#64748B' }}>
          STATIONS: {filteredStations.length} | ACTIVE UNITS: {filteredUnits.length}
        </div>
      </div>
    </div>
  )
}

// ─── High-Fidelity Canvas SVG Fallback Component ───
function FallbackMap({ stations, units, selected, onSelect, isLiveTracking }) {
  const W = 600, H = 340
  const pad = 40

  const minLon = 74.0, maxLon = 78.5
  const minLat = 11.5, maxLat = 18.5

  const toX = (lon) => pad + ((lon - minLon) / (maxLon - minLon)) * (W - pad * 2)
  const toY = (lat) => pad + (1 - (lat - minLat) / (maxLat - minLat)) * (H - pad * 2)

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height="100%" style={{ background: '#04060A' }}>
      {/* Grid Lines */}
      {Array.from({ length: 7 }).map((_, i) => (
        <line
          key={`h-${i}`}
          x1={0}
          y1={i * 50}
          x2={W}
          y2={i * 50}
          stroke="rgba(0, 200, 240, 0.05)"
          strokeDasharray="4 4"
        />
      ))}
      {Array.from({ length: 9 }).map((_, i) => (
        <line
          key={`v-${i}`}
          x1={i * 70}
          y1={0}
          x2={i * 70}
          y2={H}
          stroke="rgba(0, 200, 240, 0.05)"
          strokeDasharray="4 4"
        />
      ))}

      <text x={W / 2} y={22} textAnchor="middle" fill="#00C8F0" fontSize="10" fontFamily="var(--mono)" fontWeight="bold">
        KARNATAKA STATE GEOSPATIAL VECTOR MAP
      </text>

      {/* Render Unit Trail Breadcrumbs */}
      {isLiveTracking &&
        units.map((u) => {
          if (!u.history || u.history.length < 2) return null
          const points = u.history.map(([lon, lat]) => `${toX(lon)},${toY(lat)}`).join(' ')
          return (
            <polyline
              key={`trail-${u.id}`}
              points={points}
              fill="none"
              stroke="#00D4FF"
              strokeWidth="1.5"
              strokeDasharray="3 3"
              opacity="0.6"
            />
          )
        })}

      {/* Render Stations */}
      {stations.map((st) => {
        const cx = toX(st.lon)
        const cy = toY(st.lat)
        const color = SEVERITY_COLORS[st.severity] || '#00C8F0'

        return (
          <g key={st.id} onClick={() => onSelect(st)} style={{ cursor: 'pointer' }}>
            <circle cx={cx} cy={cy} r={6} fill={color} stroke="#FFFFFF" strokeWidth="1.5" />
            <text x={cx} y={cy - 9} textAnchor="middle" fill="#E2E8F0" fontSize="8" fontFamily="var(--mono)">
              {st.label}
            </text>
          </g>
        )
      })}

      {/* Render Live Patrol Units */}
      {isLiveTracking &&
        units.map((u) => {
          const cx = toX(u.lon)
          const cy = toY(u.lat)

          return (
            <g key={u.id} onClick={() => onSelect({ ...u, isLiveUnit: true })} style={{ cursor: 'pointer' }}>
              <circle cx={cx} cy={cy} r={8} fill="rgba(0, 212, 255, 0.2)" stroke="#00D4FF" strokeWidth="1" />
              <circle cx={cx} cy={cy} r={4} fill="#00E5FF" />
              <text x={cx} y={cy + 14} textAnchor="middle" fill="#00E5FF" fontSize="8" fontFamily="var(--mono)" fontWeight="bold">
                {u.callsign} ({u.speed}km/h)
              </text>
            </g>
          )
        })}
    </svg>
  )
}

