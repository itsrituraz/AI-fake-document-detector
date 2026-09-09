import React from 'react';
import { FileText, Check, Shield, Copy } from 'lucide-react';

export default function OcrCard({ ocr }) {
  if (!ocr) return null;

  const {
    document_type,
    fields,
    raw_mrz,
    overall_ocr_confidence
  } = ocr;

  const [copied, setCopied] = React.useState(false);

  const copyMrz = () => {
    if (raw_mrz && raw_mrz.length > 0) {
      navigator.clipboard.writeText(raw_mrz.join('\n'));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            OCR Extracted Field Metadata ({document_type || 'Document'})
          </h3>
        </div>

        <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-emerald-950/60 border border-emerald-700/60 text-emerald-300 font-bold">
          {((overall_ocr_confidence || 0) * 100).toFixed(0)}% Readability
        </span>
      </div>

      {/* Structured Fields Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-5">
        {fields && Object.entries(fields).map(([key, item]) => {
          if (!item || typeof item !== 'object' || !item.value) return null;
          const label = key.replace(/_/g, ' ').toUpperCase();
          const conf = Math.round((item.confidence || 0.85) * 100);

          return (
            <div key={key} className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
              <span className="text-[10px] font-bold text-slate-400 tracking-wider">
                {label}
              </span>
              <span className="font-mono text-xs font-semibold text-slate-100 mt-1 truncate" title={item.value}>
                {item.value}
              </span>
              <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-800/80 text-[10px] text-slate-400">
                <span className="capitalize">{item.source || 'VIZ'}</span>
                <span className={`font-mono font-medium ${
                  conf >= 90 ? 'text-emerald-400' : conf >= 70 ? 'text-cyan-400' : 'text-amber-400'
                }`}>
                  {conf}% Conf
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Raw MRZ Box (Monospace) */}
      {raw_mrz && raw_mrz.length > 0 && (
        <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Machine Readable Zone (ICAO Doc 9303 MRZ Lines):
            </span>
            <button
              type="button"
              onClick={copyMrz}
              className="text-[11px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-mono"
            >
              {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              {copied ? 'Copied' : 'Copy MRZ'}
            </button>
          </div>
          <div className="font-mono text-xs text-emerald-400 font-bold tracking-widest leading-relaxed bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 select-all overflow-x-auto">
            {raw_mrz.map((line, idx) => (
              <div key={idx} className="whitespace-pre">{line}</div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
