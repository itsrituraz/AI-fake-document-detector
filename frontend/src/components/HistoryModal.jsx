import React, { useState, useEffect } from 'react';
import { X, Search, Filter, Shield, Calendar, User, FileText, Download } from 'lucide-react';

export default function HistoryModal({ isOpen, onClose, onLoadScreening }) {
  const [history, setHistory] = useState([]);
  const [filter, setFilter] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen, filter]);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const url = filter ? `/api/history?risk_filter=${filter}` : '/api/history';
      const res = await fetch(url);
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = async (id) => {
    try {
      const res = await fetch(`/api/history/${id}`);
      const record = await res.json();
      if (record && record.report) {
        onLoadScreening(record.report);
        onClose();
      }
    } catch (err) {
      alert('Failed to load past screening: ' + err.message);
    }
  };

  if (!isOpen) return null;

  const filtered = history.filter((item) => {
    const term = searchTerm.toLowerCase();
    return (
      (item.document_number && item.document_number.toLowerCase().includes(term)) ||
      (item.holder_name && item.holder_name.toLowerCase().includes(term)) ||
      (item.document_type && item.document_type.toLowerCase().includes(term))
    );
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-panel w-full max-w-4xl max-h-[85vh] rounded-2xl flex flex-col border border-slate-700 shadow-2xl overflow-hidden">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/60">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Shield className="w-4 h-4 text-cyan-400" />
              Border Checkpoint Screening Audit Log
            </h2>
            <p className="text-xs text-slate-400">
              Historical ledger stored in SQLite permanent registry.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter Controls */}
        <div className="p-3 border-b border-slate-800 bg-slate-900/40 flex flex-wrap items-center justify-between gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by Document No or Holder Name..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500"
            />
          </div>

          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-slate-400 text-[11px] font-medium mr-1">Risk Filter:</span>
            {['ALL', 'LOW', 'MEDIUM', 'HIGH'].map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setFilter(t === 'ALL' ? null : t)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors ${
                  (t === 'ALL' && filter === null) || filter === t
                    ? 'bg-cyan-500 text-slate-950 font-bold'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* History Records Table */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="text-center py-12 text-xs text-slate-400">
              Loading historical screenings...
            </div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-12 text-xs text-slate-400">
              No matching screening records found in database.
            </div>
          ) : (
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold text-[11px] uppercase tracking-wider">
                  <th className="pb-2.5">ID</th>
                  <th className="pb-2.5">Timestamp</th>
                  <th className="pb-2.5">Doc No.</th>
                  <th className="pb-2.5">Holder Name</th>
                  <th className="pb-2.5">Type</th>
                  <th className="pb-2.5">Risk Score</th>
                  <th className="pb-2.5">Verdict</th>
                  <th className="pb-2.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filtered.map((row) => {
                  const riskColor =
                    row.risk_tier === 'HIGH'
                      ? 'text-red-400 bg-red-950/40 border-red-800'
                      : row.risk_tier === 'MEDIUM'
                      ? 'text-amber-400 bg-amber-950/40 border-amber-800'
                      : 'text-emerald-400 bg-emerald-950/40 border-emerald-800';

                  return (
                    <tr key={row.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-2.5 font-mono text-slate-400">#{row.id}</td>
                      <td className="py-2.5 text-slate-400">
                        {new Date(row.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td className="py-2.5 font-mono font-bold text-slate-200">{row.document_number}</td>
                      <td className="py-2.5 text-slate-300">{row.holder_name}</td>
                      <td className="py-2.5 uppercase text-slate-400 text-[10px]">{row.document_type}</td>
                      <td className="py-2.5 font-mono font-bold">
                        <span className={`px-2 py-0.5 rounded border text-[11px] ${riskColor}`}>
                          {row.overall_risk_score.toFixed(0)} ({row.risk_tier})
                        </span>
                      </td>
                      <td className="py-2.5">
                        <span className="text-[10px] uppercase font-bold text-slate-400">
                          {row.decision}
                        </span>
                      </td>
                      <td className="py-2.5 text-right">
                        <button
                          type="button"
                          onClick={() => handleSelect(row.id)}
                          className="px-2.5 py-1 bg-cyan-950 hover:bg-cyan-900 border border-cyan-700/60 text-cyan-300 rounded text-xs font-medium cursor-pointer"
                        >
                          Load Details
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

      </div>
    </div>
  );
}
