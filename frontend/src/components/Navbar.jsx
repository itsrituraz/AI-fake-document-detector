import React from 'react';
import { ShieldCheck, Database, Radio, History, Sparkles } from 'lucide-react';

export default function Navbar({ onOpenHistory, onSelectPreset, presets, activePreset }) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* System Branding */}
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-400 via-cyan-500 to-emerald-600 shadow-lg shadow-cyan-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                BORDER SENTRY <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 border border-cyan-800/60 text-cyan-300 font-mono">v1.0</span>
              </h1>
            </div>
            <p className="text-xs text-slate-400">
              AI Powered Identity & Document Verification 
            </p>
          </div>
        </div>

        {/* Status Indicators & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          
          {/* Checkpoint Status Badges */}
          <div className="hidden sm:flex items-center gap-3 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              LANE 03 // ACTIVE
            </span>
            <span className="text-slate-600">|</span>
            <span className="flex items-center gap-1.5 text-slate-300">
              <Database className="w-3.5 h-3.5 text-teal-400" />
              REFERENCE WATCHLIST: READY
            </span>
          </div>

          {/* Preset Selector Dropdown */}
          <div className="flex items-center gap-2">
            <div className="relative">
              <select
                value={activePreset || ''}
                onChange={(e) => onSelectPreset(e.target.value)}
                className="text-xs bg-slate-900 hover:bg-slate-800 border border-teal-500/30 text-teal-300 font-medium py-1.5 px-3 pr-8 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-cyan-500 transition-colors"
              >
                <option value="">-- Load Demo Specimen --</option>
                {presets && presets.map((p) => (
                  <option key={p.file} value={p.file}>
                    {p.label}
                  </option>
                ))}
              </select>
              <Sparkles className="w-3.5 h-3.5 text-teal-400 absolute right-2.5 top-2.5 pointer-events-none" />
            </div>

            {/* Audit History Drawer Button */}
            <button
              onClick={onOpenHistory}
              className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors shadow-sm"
              title="View Screening Audit Trail"
            >
              <History className="w-3.5 h-3.5 text-slate-400" />
              <span>Audit Log</span>
            </button>
          </div>

        </div>

      </div>
    </header>
  );
}
