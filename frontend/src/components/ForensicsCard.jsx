import React from 'react';
import { Flame, Type, FileSearch, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function ForensicsCard({ forensics }) {
  if (!forensics) return null;

  const {
    tampering_score,
    is_tampered,
    sub_detector_scores,
    triggers,
    explanation,
    ela_details,
    font_details,
    metadata_details,
    stamp_details
  } = forensics;

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <Flame className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Multi-Signal Forensic Tampering Analysis
          </h3>
        </div>

        <span
          className={`text-xs px-2.5 py-1 rounded-md font-bold uppercase tracking-wider ${
            is_tampered
              ? 'bg-red-950/60 text-red-300 border border-red-700/60'
              : 'bg-emerald-950/60 text-emerald-300 border border-emerald-700/60'
          }`}
        >
          {tampering_score.toFixed(0)}% Tampering Likelihood
        </span>
      </div>

      {/* 4 Sub-Detector Matrix */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        
        {/* 1. Error Level Analysis (ELA) */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <Flame className="w-3.5 h-3.5 text-amber-400" />
              Error Level Analysis (ELA)
            </span>
            <span className="font-mono text-slate-200 font-bold">{sub_detector_scores?.ela}%</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Photo Discrepancy: <span className="font-mono text-slate-300">{ela_details?.photo_region_anomaly}x</span> | Max Spike: <span className="font-mono text-slate-300">{ela_details?.max_local_discrepancy}x</span>
          </p>
        </div>

        {/* 2. Typography & Font Consistency */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <Type className="w-3.5 h-3.5 text-blue-400" />
              Font & Baseline Consistency
            </span>
            <span className="font-mono text-slate-200 font-bold">{sub_detector_scores?.font}%</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Baseline Deviation: <span className="font-mono text-slate-300">{font_details?.baseline_deviation_px}px</span> | Height Var: <span className="font-mono text-slate-300">{font_details?.height_variance}</span>
          </p>
        </div>

        {/* 3. EXIF & Metadata Integrity */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <FileSearch className="w-3.5 h-3.5 text-purple-400" />
              Metadata & EXIF Forensics
            </span>
            <span className="font-mono text-slate-200 font-bold">{sub_detector_scores?.metadata}%</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Editor Tag: <span className="font-mono text-slate-300">{metadata_details?.software_signature || 'None Detected'}</span>
          </p>
        </div>

        {/* 4. Circular Stamp & Seal Verification */}
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-slate-300 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Consular Seal / Stamp Match
            </span>
            <span className="font-mono text-slate-200 font-bold">{((stamp_details?.similarity_score || 0) * 100).toFixed(0)}%</span>
          </div>
          <p className="text-[11px] text-slate-400">
            Status: <span className="font-mono text-slate-300">{stamp_details?.is_verified ? 'Template Correlated' : 'Discrepancy'}</span>
          </p>
        </div>

      </div>

      {/* Triggers & Explanations */}
      <div className="space-y-1.5 pt-2 border-t border-slate-800/80 text-xs">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Forensic Explanation:
        </span>
        <p className="text-slate-200 font-medium leading-relaxed">
          {explanation}
        </p>

        {triggers?.length > 0 && (
          <div className="mt-2 space-y-1">
            {triggers.map((trig, idx) => (
              <div key={idx} className="flex items-start gap-1.5 text-red-300 bg-red-950/30 border border-red-900/40 px-2.5 py-1 rounded-md">
                <AlertTriangle className="w-3.5 h-3.5 text-red-400 shrink-0 mt-0.5" />
                <span>{trig}</span>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
