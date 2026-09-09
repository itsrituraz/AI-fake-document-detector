import React from 'react';
import { UserCheck, UserX, UserMinus, ShieldAlert, Cpu } from 'lucide-react';

export default function BiometricsCard({ biometrics }) {
  if (!biometrics) return null;

  const {
    is_matched,
    similarity_percentage,
    l2_distance,
    verdict,
    explanation,
    document_face_thumbnail,
    selfie_face_thumbnail,
    flags
  } = biometrics;

  const isConfirmed = verdict === 'MATCH_CONFIRMED';
  const isMismatch = verdict === 'MISMATCH_ALERT';

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <UserCheck className="w-4 h-4 text-blue-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Biometric 1:1 Facial Verification
          </h3>
        </div>

        {/* Verdict Badge */}
        <span
          className={`text-xs px-2.5 py-1 rounded-md font-bold uppercase tracking-wider flex items-center gap-1 ${
            isConfirmed
              ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-700/60'
              : isMismatch
              ? 'bg-red-950/60 text-red-300 border border-red-700/60 animate-pulse'
              : 'bg-slate-900 text-slate-400 border border-slate-700'
          }`}
        >
          {isConfirmed && <UserCheck className="w-3.5 h-3.5" />}
          {isMismatch && <UserX className="w-3.5 h-3.5" />}
          {verdict.replace(/_/g, ' ')}
        </span>
      </div>

      {/* Side-by-Side Face Comparison */}
      <div className="grid grid-cols-2 gap-4 items-center justify-center mb-4">
        
        {/* Document Portrait */}
        <div className="flex flex-col items-center text-center p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            ID Document Photo
          </span>
          {document_face_thumbnail ? (
            <img
              src={document_face_thumbnail}
              alt="Document face"
              className="w-24 h-24 sm:w-28 sm:h-28 object-cover rounded-xl border border-slate-700 shadow-md"
            />
          ) : (
            <div className="w-24 h-24 rounded-xl bg-slate-800 flex items-center justify-center text-slate-500">
              <UserMinus className="w-8 h-8" />
            </div>
          )}
        </div>

        {/* Live Selfie */}
        <div className="flex flex-col items-center text-center p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Live Selfie Capture
          </span>
          {selfie_face_thumbnail ? (
            <img
              src={selfie_face_thumbnail}
              alt="Selfie face"
              className="w-24 h-24 sm:w-28 sm:h-28 object-cover rounded-xl border border-slate-700 shadow-md"
            />
          ) : (
            <div className="w-24 h-24 rounded-xl bg-slate-800 flex flex-col items-center justify-center text-slate-500 text-xs p-2">
              <UserMinus className="w-6 h-6 mb-1" />
              <span>No Selfie</span>
            </div>
          )}
        </div>

      </div>

      {/* Similarity Meter */}
      <div className="space-y-1.5 p-3 rounded-xl bg-slate-900/40 border border-slate-800/80 mb-3">
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-400 font-medium">Embedding Cosine Similarity:</span>
          <span className={`font-mono font-bold text-sm ${
            isConfirmed ? 'text-emerald-400' : isMismatch ? 'text-red-400' : 'text-slate-300'
          }`}>
            {similarity_percentage ? `${similarity_percentage.toFixed(1)}%` : 'N/A'}
          </span>
        </div>
        <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-700 ${
              isConfirmed ? 'bg-emerald-500' : isMismatch ? 'bg-red-500' : 'bg-slate-600'
            }`}
            style={{ width: `${similarity_percentage || 0}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-slate-500">
          <span>0% (Impostor)</span>
          <span>Threshold: 65%</span>
          <span>100% (Identical)</span>
        </div>
      </div>

      {/* Metric Details */}
      <div className="text-xs space-y-1 text-slate-300">
        <p className="font-medium text-slate-200">{explanation}</p>
        {l2_distance !== undefined && (
          <p className="text-[11px] text-slate-400 font-mono">
            Euclidean L2 Distance: {l2_distance.toFixed(3)}
          </p>
        )}
      </div>

    </div>
  );
}
