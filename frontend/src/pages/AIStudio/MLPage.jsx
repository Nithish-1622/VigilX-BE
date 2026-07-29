import { useState } from 'react'
import { motion } from 'framer-motion'
import { Brain, Upload, Play, Settings, Cpu, HardDrive, Activity, CheckCircle2, Clock, Plus, Database } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const DUMMY_LOSS_DATA = [
  { epoch: 1, train_loss: 2.4, val_loss: 2.5 },
  { epoch: 2, train_loss: 1.8, val_loss: 1.9 },
  { epoch: 3, train_loss: 1.2, val_loss: 1.4 },
  { epoch: 4, train_loss: 0.9, val_loss: 1.1 },
  { epoch: 5, train_loss: 0.7, val_loss: 0.9 },
  { epoch: 6, train_loss: 0.5, val_loss: 0.8 },
  { epoch: 7, train_loss: 0.4, val_loss: 0.75 },
  { epoch: 8, train_loss: 0.35, val_loss: 0.7 },
  { epoch: 9, train_loss: 0.3, val_loss: 0.68 },
  { epoch: 10, train_loss: 0.25, val_loss: 0.65 },
]

export default function MLPage() {
  return (
    <div className="space-y-8 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header Banner */}
      <div className="rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden"
        style={{ border: '1px solid rgba(191,90,242,0.2)', background: 'linear-gradient(135deg, rgba(191,90,242,0.08) 0%, rgba(191,90,242,0.02) 100%)' }}
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[rgba(191,90,242,0.5)] to-transparent"></div>
        
        <div className="w-16 h-16 shrink-0 rounded-2xl flex items-center justify-center shadow-lg"
          style={{ background: 'rgba(191,90,242,0.15)', border: '1px solid rgba(191,90,242,0.3)' }}
        >
          <Brain size={32} style={{ color: 'var(--accent-purple, #bf5af2)' }} className="drop-shadow-md" />
        </div>
        
        <div className="flex-1 text-center md:text-left">
          <h2 className="text-2xl font-bold text-white tracking-tight mb-1">ML Training Studio</h2>
          <p className="text-gray-400 text-sm">Active model training pipeline for Suspect Profiling AI (v2.4).</p>
        </div>
        
        <div className="flex gap-4 w-full md:w-auto mt-4 md:mt-0 justify-center">
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all bg-white/5 border border-white/10 hover:bg-white/10 text-white">
            <Upload size={16} /> Dataset
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{ background: 'var(--accent-purple, #bf5af2)', color: 'white' }}
          >
            <Plus size={16} /> New Job
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Active Run & Metrics */}
        <div className="lg:col-span-2 space-y-8">
          {/* Active Run Card */}
          <div className="rounded-2xl border border-white/10 bg-[#0B0C10]/80 p-6 backdrop-blur-md">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Activity size={18} className="text-green-400" />
                  Active Run: SuspectProfile-v2.4
                </h3>
                <p className="text-xs text-gray-400 mt-1">Started 2 hours ago • ResNet50 Backbone • Epoch 10/50</p>
              </div>
              <div className="flex gap-2">
                <button className="p-2 rounded-md bg-white/5 border border-white/10 hover:bg-white/10 text-white"><Settings size={16}/></button>
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30">
                   Stop Run
                </button>
              </div>
            </div>

            {/* Metrics Chart */}
            <div className="h-64 w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={DUMMY_LOSS_DATA} margin={{ top: 10, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="epoch" stroke="#666" tick={{fill: '#666', fontSize: 12}} />
                  <YAxis stroke="#666" tick={{fill: '#666', fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#111', borderColor: '#333', borderRadius: '8px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Line type="monotone" dataKey="train_loss" name="Training Loss" stroke="#bf5af2" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="val_loss" name="Validation Loss" stroke="#00f2fe" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Quick Actions Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon: Database, label: 'Manage Datasets', desc: '14 Datasets • 2.4 TB total' },
              { icon: Settings, label: 'Model Architectures', desc: '8 saved configurations' },
              { icon: Activity, label: 'Evaluation Metrics', desc: 'View inference reports' },
            ].map((f) => (
              <div key={f.label} className="rounded-2xl p-6 flex flex-col items-start border border-white/5 bg-white/5 hover:bg-white/10 transition-colors cursor-pointer group">
                <f.icon size={20} className="mb-3 text-gray-300" />
                <h3 className="text-sm font-semibold text-white mb-1">{f.label}</h3>
                <p className="text-xs text-gray-400">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Cluster Status & History */}
        <div className="space-y-8">
          {/* Cluster Status */}
          <div className="rounded-2xl border border-white/10 bg-[#0B0C10]/80 p-6 backdrop-blur-md">
            <h3 className="text-sm font-semibold text-white mb-4">Cluster Status</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400 flex items-center gap-1"><Cpu size={14}/> GPU Utilization (4x A100)</span>
                  <span className="text-green-400">92%</span>
                </div>
                <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-green-500 to-emerald-400 w-[92%] rounded-full"></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400 flex items-center gap-1"><HardDrive size={14}/> VRAM Usage</span>
                  <span className="text-yellow-400">76GB / 80GB</span>
                </div>
                <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-yellow-500 to-orange-400 w-[95%] rounded-full"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Jobs */}
          <div className="rounded-2xl border border-white/10 bg-[#0B0C10]/80 p-6 backdrop-blur-md">
            <h3 className="text-sm font-semibold text-white mb-4">Recent Jobs</h3>
            <div className="space-y-3">
              {[
                { name: 'NLP-NER-FinTuning', status: 'completed', time: '5h ago' },
                { name: 'Audio-Speech-v1', status: 'completed', time: '1d ago' },
                { name: 'Vision-Anomaly-Det', status: 'failed', time: '2d ago' },
              ].map((job, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="flex items-center gap-3">
                    {job.status === 'completed' ? (
                      <CheckCircle2 size={16} className="text-green-500" />
                    ) : (
                      <Clock size={16} className="text-red-500" />
                    )}
                    <div>
                      <p className="text-xs font-medium text-white">{job.name}</p>
                      <p className="text-[10px] text-gray-500">{job.time}</p>
                    </div>
                  </div>
                  <span className="text-[10px] uppercase tracking-wider font-semibold text-gray-400">
                    {job.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
