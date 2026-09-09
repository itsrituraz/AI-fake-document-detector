import React from 'react';
import { CheckCircle2, XCircle, AlertCircle, Database, Calendar, Globe, Key } from 'lucide-react';

export default function ValidationCard({ validation }) {
  if (!validation) return null;

  const {
    is_valid,
    validation_score,
    mrz_checks,
    date_checks,
    country_checks,
    cross_zone_checks,
    watchlist_checks,
    critical_violations
  } = validation;

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <Key className="w-4 h-4 text-purple-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Cryptographic & Logic Rule Verification
          </h3>
        </div>

        <span
          className={`text-xs px-2.5 py-1 rounded-md font-bold uppercase tracking-wider ${
            is_valid
              ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-700/60'
              : 'bg-red-950/60 text-red-300 border border-red-700/60'
          }`}
        >
          {((validation_score || 0) * 100).toFixed(0)}% Rule Compliance
        </span>
      </div>

      {/* Validation Checklist Items */}
      <div className="space-y-2.5 mb-4 text-xs">
        
        {/* 1. MRZ Checksum Status */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-slate-300">
            <Key className="w-4 h-4 text-purple-400" />
            <span>ICAO Doc 9303 Checksum Algorithms (7-3-1 Modulo 10):</span>
          </div>
          <span className={`font-semibold flex items-center gap-1 ${
            mrz_checks?.is_valid ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {mrz_checks?.is_valid ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
            {mrz_checks?.passed_checks}/{mrz_checks?.total_checks} Check Digits Passed
          </span>
        </div>

        {/* 2. Date Chronology Logic */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-slate-300">
            <Calendar className="w-4 h-4 text-cyan-400" />
            <span>Date Chronology (Expiry &gt; Issue &gt; DOB):</span>
          </div>
          <span className={`font-semibold flex items-center gap-1 ${
            date_checks?.is_valid ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {date_checks?.is_valid ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
            {date_checks?.is_expired ? 'EXPIRED' : date_checks?.is_valid ? 'Chronologically Valid' : 'Date Conflict'}
          </span>
        </div>

        {/* 3. ISO Country Code */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-slate-300">
            <Globe className="w-4 h-4 text-blue-400" />
            <span>ISO 3166-1 Alpha-3 State & Nationality Code:</span>
          </div>
          <span className={`font-semibold flex items-center gap-1 ${
            country_checks?.is_valid ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {country_checks?.is_valid ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
            {country_checks?.code || 'Valid Standard Code'}
          </span>
        </div>

        {/* 4. Mock Watchlist / Interpol SLTD Database Query */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-slate-300">
            <Database className="w-4 h-4 text-amber-400" />
            <span>Interpol SLTD & Stolen Identity Watchlist:</span>
          </div>
          <span className={`font-semibold flex items-center gap-1 ${
            watchlist_checks?.alert_level === 'CRITICAL'
              ? 'text-red-400 animate-pulse font-bold'
              : 'text-emerald-400'
          }`}>
            {watchlist_checks?.alert_level === 'CRITICAL' ? (
              <>
                <XCircle className="w-3.5 h-3.5" />
                CRITICAL HIT
              </>
            ) : (
              <>
                <CheckCircle2 className="w-3.5 h-3.5" />
                CLEARED
              </>
            )}
          </span>
        </div>

        {/* 5. Cross-Zone Consistency (MRZ vs VIZ) */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-slate-300">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Cross-Zone Consistency (Printed VIZ vs MRZ):</span>
          </div>
          <span className={`font-semibold flex items-center gap-1 ${
            cross_zone_checks?.is_consistent ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {cross_zone_checks?.is_consistent ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
            {cross_zone_checks?.is_consistent ? 'Consistent' : 'Discrepancy Detected'}
          </span>
        </div>

      </div>

      {/* Critical Violations Alert Banner */}
      {critical_violations?.length > 0 && (
        <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
          {critical_violations.map((viol, idx) => (
            <div key={idx} className="flex items-start gap-1.5 text-xs text-red-300 bg-red-950/40 border border-red-800/50 p-2 rounded-lg">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <span>{viol}</span>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
