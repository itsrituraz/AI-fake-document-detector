import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Send, Check } from 'lucide-react';

export default function OfficerDecisionConsole({ screeningId, onDecisionRecorded }) {
  const [notes, setNotes] = useState('');
  const [decision, setDecision] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  if (!screeningId || screeningId === -1) return null;

  const handleAction = async (action) => {
    setIsSubmitting(true);
    setDecision(action);
    try {
      const res = await fetch(`/api/history/${screeningId}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision: action,
          officer_notes: notes
        })
      });
      if (res.ok) {
        setSavedSuccess(true);
        if (onDecisionRecorded) onDecisionRecorded(action);
        setTimeout(() => setSavedSuccess(false), 3000);
      }
    } catch (err) {
      alert('Failed to record officer decision: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 mb-8">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Border Officer Decision Console (Screening #{screeningId})
          </h3>
          <p className="text-xs text-slate-400">
            Record officer determination and audit notes into the permanent registry.
          </p>
        </div>

        {savedSuccess && (
          <span className="text-xs font-medium px-2.5 py-1 rounded bg-emerald-950/80 border border-emerald-700 text-emerald-300 flex items-center gap-1 animate-fade-in">
            <Check className="w-3.5 h-3.5" /> Verdict Logged
          </span>
        )}
      </div>

      <div className="space-y-3">
        {/* Notes Input */}
        <div>
          <label className="text-xs text-slate-400 font-medium mb-1 block">
            Inspector Findings & Justification Notes:
          </label>
          <textarea
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Enter officer tactile examination findings, physical security observations, or interview notes..."
            className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500 placeholder-slate-500 resize-none"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3 pt-1">
          
          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleAction('APPROVED')}
            className={`flex-1 min-w-[140px] py-2.5 px-3 rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md cursor-pointer ${
              decision === 'APPROVED' && savedSuccess
                ? 'bg-emerald-600 text-white ring-2 ring-emerald-400'
                : 'bg-emerald-950/60 hover:bg-emerald-900 text-emerald-300 border border-emerald-700/60'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" />
            Approve Document
          </button>

          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleAction('ESCALATED')}
            className={`flex-1 min-w-[140px] py-2.5 px-3 rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md cursor-pointer ${
              decision === 'ESCALATED' && savedSuccess
                ? 'bg-amber-600 text-white ring-2 ring-amber-400'
                : 'bg-amber-950/60 hover:bg-amber-900 text-amber-300 border border-amber-700/60'
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
            Secondary Inspection
          </button>

          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleAction('REJECTED')}
            className={`flex-1 min-w-[140px] py-2.5 px-3 rounded-xl font-bold text-xs flex items-center justify-center gap-1.5 transition-all shadow-md cursor-pointer ${
              decision === 'REJECTED' && savedSuccess
                ? 'bg-red-600 text-white ring-2 ring-red-400'
                : 'bg-red-950/60 hover:bg-red-900 text-red-300 border border-red-700/60'
            }`}
          >
            <XCircle className="w-4 h-4" />
            Reject & Impound
          </button>

        </div>
      </div>
    </div>
  );
}
