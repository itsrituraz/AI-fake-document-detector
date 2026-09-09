import React from 'react';
import { ShieldCheck, Lock } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-slate-800 bg-gradient-to-b from-slate-950 via-[#070b14] to-[#070b14] px-4 lg:px-8 py-10 lg:py-14">

      {/* Ambient background glow */}
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div className="absolute -top-24 right-1/3 w-96 h-96 rounded-full bg-teal-500/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-72 h-72 rounded-full bg-cyan-500/10 blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto flex flex-col lg:flex-row items-center justify-between gap-8">

        {/* Headline */}
        <div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
            AI-Powered
            <br />
            <span className="bg-gradient-to-r from-teal-300 via-cyan-300 to-emerald-300 bg-clip-text text-transparent">
              Identity Verification
            </span>
          </h2>

          <div className="mt-4 flex items-center gap-3">
            <span className="h-px w-10 bg-teal-500/50" />
            <p className="text-sm tracking-[0.2em] text-slate-400 font-medium uppercase">
              Detect &bull; Verify &bull; Prevent
            </p>
          </div>
        </div>

        {/* Trust badge + caption */}
        <div className="flex items-center gap-6">
          <div className="text-right hidden sm:block">
            <p className="text-sm tracking-[0.25em] text-teal-300 font-semibold uppercase">
              Trusted Identities
            </p>
            <p className="text-sm tracking-[0.25em] text-slate-400 font-medium uppercase">
              Stronger Borders
            </p>
          </div>

          <div className="relative flex items-center justify-center w-24 h-24 shrink-0">
            <span className="absolute inset-0 rounded-full border-2 border-teal-500/15 border-t-teal-400/70 animate-[spin_6s_linear_infinite]" />
            <div className="relative flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-teal-400 via-cyan-500 to-emerald-600 shadow-lg shadow-cyan-500/30">
              <ShieldCheck className="w-7 h-7 text-white" />
              <span className="absolute -bottom-1.5 -right-1.5 flex items-center justify-center w-6 h-6 rounded-full bg-slate-950 border border-teal-500/40">
                <Lock className="w-3 h-3 text-teal-300" />
              </span>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
