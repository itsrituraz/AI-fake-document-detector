import React from 'react';
import {
  AlertOctagon,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  Cpu,
} from 'lucide-react';

export default function RiskGauge({ assessment }) {
  if (!assessment) return null;

  const {
    overall_risk_score,
    risk_tier,
    risk_color,
    recommendation,
    breakdown,
    summary_signals,
  } = assessment;

  // =========================================================
  // GAUGE CALCULATION
  // =========================================================

  const radius = 54;
  const circumference = 2 * Math.PI * radius;

  const score = Math.max(
    0,
    Math.min(100, Number(overall_risk_score) || 0)
  );

  const strokeDashoffset =
    circumference - (score / 100) * circumference;

  // =========================================================
  // RISK THEMES
  // =========================================================

  const colorMap = {
    green: {
      text: 'text-emerald-400',
      bg: 'bg-emerald-950/30',
      border: 'border-emerald-700/50',
      stroke: '#10b981',
      badge:
        'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
      glow: 'shadow-emerald-500/10',
      dot: 'bg-emerald-400',
    },

    amber: {
      text: 'text-amber-400',
      bg: 'bg-amber-950/30',
      border: 'border-amber-700/50',
      stroke: '#f59e0b',
      badge:
        'bg-amber-500/10 text-amber-300 border-amber-500/30',
      glow: 'shadow-amber-500/10',
      dot: 'bg-amber-400',
    },

    red: {
      text: 'text-red-400',
      bg: 'bg-red-950/30',
      border: 'border-red-700/50',
      stroke: '#ef4444',
      badge:
        'bg-red-500/10 text-red-300 border-red-500/30',
      glow: 'shadow-red-500/10',
      dot: 'bg-red-400',
    },
  };

  const currentTheme =
    colorMap[risk_color] || colorMap.green;

  // =========================================================
  // ICON BASED ON RISK
  // =========================================================

  const RiskIcon =
    risk_tier === 'HIGH'
      ? ShieldAlert
      : risk_tier === 'MEDIUM'
      ? AlertTriangle
      : CheckCircle2;

  // =========================================================
  // SAFE BREAKDOWN VALUES
  // =========================================================

  const forensicContribution =
    Number(breakdown?.tampering_contribution) || 0;

  const biometricContribution =
    Number(breakdown?.biometrics_contribution) || 0;

  const validationContribution =
    Number(breakdown?.validation_contribution) || 0;

  const ocrContribution =
    Number(breakdown?.ocr_contribution) || 0;

  return (
    <div
      className={`
        glass-panel
        rounded-2xl
        p-5
        lg:p-6
        mb-8

        border
        ${currentTheme.border}

        bg-slate-950/30

        shadow-[0_0_45px_rgba(20,184,166,0.035)]

        transition-all
        duration-500
      `}
    >

      {/* ===================================================== */}
      {/* TOP SECTION */}
      {/* ===================================================== */}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">

        {/* =================================================== */}
        {/* RISK GAUGE */}
        {/* =================================================== */}

        <div className="md:col-span-4 flex items-center justify-center gap-5">

          <div className="relative w-36 h-36 flex items-center justify-center">

            <svg
              className="w-full h-full transform -rotate-90"
              viewBox="0 0 130 130"
            >

              {/* Background ring */}
              <circle
                cx="65"
                cy="65"
                r={radius}
                className="stroke-slate-800"
                strokeWidth="10"
                fill="transparent"
              />

              {/* Progress ring */}
              <circle
                cx="65"
                cy="65"
                r={radius}
                stroke={currentTheme.stroke}
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="
                  transition-all
                  duration-1000
                  ease-out
                  drop-shadow-[0_0_7px_rgba(20,184,166,0.25)]
                "
              />

            </svg>

            {/* Center number */}
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">

              <span
                className={`
                  text-3xl
                  font-black
                  font-mono
                  tracking-tight
                  ${currentTheme.text}
                `}
              >
                {score.toFixed(0)}
              </span>

              <span
                className="
                  text-[10px]
                  uppercase
                  tracking-[0.18em]
                  font-semibold
                  text-slate-500
                "
              >
                Risk Score
              </span>

            </div>

          </div>


          {/* Risk label */}
          <div className="space-y-2">

            <span
              className={`
                inline-flex
                items-center
                px-2.5
                py-1
                rounded-md
                text-xs
                font-bold
                uppercase
                tracking-wider
                border
                ${currentTheme.badge}
              `}
            >
              <RiskIcon className="w-3.5 h-3.5 mr-1.5" />

              {risk_tier} RISK
            </span>

            <p className="text-xs text-slate-500">
              Composite Screening Index
            </p>

            <p className="text-[10px] text-slate-600 font-mono">
              SCALE: 0 — 100
            </p>

          </div>

        </div>


        {/* =================================================== */}
        {/* OFFICER RECOMMENDATION */}
        {/* =================================================== */}

        <div className="md:col-span-8 flex flex-col justify-between h-full space-y-4">

          {/* Recommendation box */}
          <div
            className={`
              p-4
              rounded-xl
              border
              ${currentTheme.bg}
              ${currentTheme.border}
              shadow-lg
              ${currentTheme.glow}
            `}
          >

            <div className="flex items-start gap-3">

              {risk_tier === 'HIGH' ? (
                <AlertOctagon className="w-6 h-6 text-red-400 shrink-0 mt-0.5" />
              ) : risk_tier === 'MEDIUM' ? (
                <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
              ) : (
                <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
              )}

              <div className="space-y-1">

                <h3
                  className="
                    text-[11px]
                    font-bold
                    uppercase
                    tracking-[0.16em]
                    text-slate-400
                  "
                >
                  Officer Action Directive
                </h3>

                <p className="text-sm font-semibold leading-relaxed text-white">
                  {recommendation}
                </p>

              </div>

            </div>

          </div>


          {/* ================================================= */}
          {/* SECURITY SIGNALS */}
          {/* ================================================= */}

          <div className="space-y-2">

            <div
              className="
                flex
                items-center
                gap-2
                text-[11px]
                font-semibold
                text-slate-400
                uppercase
                tracking-[0.15em]
              "
            >
              <span
                className={`
                  w-1.5
                  h-1.5
                  rounded-full
                  ${currentTheme.dot}
                  shadow-[0_0_8px_rgba(20,184,166,0.5)]
                `}
              />

              Primary System Signals
            </div>


            <ul className="space-y-1.5">

              {summary_signals?.length > 0 ? (
                summary_signals.map((sig, idx) => (
                  <li
                    key={idx}
                    className="
                      flex
                      items-start
                      gap-2
                      text-xs
                      text-slate-300
                    "
                  >

                    <span
                      className={`
                        inline-block
                        w-1.5
                        h-1.5
                        rounded-full
                        mt-1.5
                        shrink-0
                        ${currentTheme.dot}
                      `}
                    />

                    <span className="leading-relaxed">
                      {sig}
                    </span>

                  </li>
                ))
              ) : (
                <li className="text-xs text-slate-500">
                  No major security signals detected.
                </li>
              )}

            </ul>

          </div>

        </div>

      </div>


      {/* ===================================================== */}
      {/* FACTOR CONTRIBUTION BREAKDOWN */}
      {/* ===================================================== */}

      <div className="mt-6 pt-5 border-t border-slate-800/80">

        <h4
          className="
            text-xs
            font-semibold
            text-slate-400
            uppercase
            tracking-[0.15em]
            mb-4
            flex
            items-center
            gap-1.5
          "
        >
          <Cpu className="w-3.5 h-3.5 text-teal-400" />

          Factor Contribution Breakdown
        </h4>


        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">


          {/* ================================================= */}
          {/* FORENSICS */}
          {/* ================================================= */}

          <div
            className="
              bg-slate-900/60
              p-3
              rounded-xl
              border
              border-slate-800/80
              hover:border-teal-500/20
              transition-colors
            "
          >

            <div className="flex justify-between text-xs mb-2">

              <span className="text-slate-400">
                Forensics
              </span>

              <span className="font-mono font-medium text-slate-200">
                {forensicContribution} pts
              </span>

            </div>

            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">

              <div
                className="
                  h-full
                  bg-gradient-to-r
                  from-teal-400
                  to-cyan-400
                  rounded-full
                  transition-all
                  duration-700
                "
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(
                      0,
                      (forensicContribution / 40) * 100
                    )
                  )}%`,
                }}
              />

            </div>

            <div className="text-[10px] text-slate-600 mt-1">
              Weight: 40%
            </div>

          </div>


          {/* ================================================= */}
          {/* BIOMETRICS */}
          {/* ================================================= */}

          <div
            className="
              bg-slate-900/60
              p-3
              rounded-xl
              border
              border-slate-800/80
              hover:border-teal-500/20
              transition-colors
            "
          >

            <div className="flex justify-between text-xs mb-2">

              <span className="text-slate-400">
                Biometrics
              </span>

              <span className="font-mono font-medium text-slate-200">
                {biometricContribution} pts
              </span>

            </div>

            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">

              <div
                className="
                  h-full
                  bg-gradient-to-r
                  from-cyan-400
                  to-sky-400
                  rounded-full
                  transition-all
                  duration-700
                "
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(
                      0,
                      (biometricContribution / 30) * 100
                    )
                  )}%`,
                }}
              />

            </div>

            <div className="text-[10px] text-slate-600 mt-1">
              Weight: 30%
            </div>

          </div>


          {/* ================================================= */}
          {/* VALIDATION */}
          {/* ================================================= */}

          <div
            className="
              bg-slate-900/60
              p-3
              rounded-xl
              border
              border-slate-800/80
              hover:border-teal-500/20
              transition-colors
            "
          >

            <div className="flex justify-between text-xs mb-2">

              <span className="text-slate-400">
                Validation
              </span>

              <span className="font-mono font-medium text-slate-200">
                {validationContribution} pts
              </span>

            </div>

            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">

              <div
                className="
                  h-full
                  bg-gradient-to-r
                  from-teal-500
                  to-emerald-400
                  rounded-full
                  transition-all
                  duration-700
                "
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(
                      0,
                      (validationContribution / 20) * 100
                    )
                  )}%`,
                }}
              />

            </div>

            <div className="text-[10px] text-slate-600 mt-1">
              Weight: 20%
            </div>

          </div>


          {/* ================================================= */}
          {/* OCR */}
          {/* ================================================= */}

          <div
            className="
              bg-slate-900/60
              p-3
              rounded-xl
              border
              border-slate-800/80
              hover:border-teal-500/20
              transition-colors
            "
          >

            <div className="flex justify-between text-xs mb-2">

              <span className="text-slate-400">
                OCR Read
              </span>

              <span className="font-mono font-medium text-slate-200">
                {ocrContribution} pts
              </span>

            </div>

            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">

              <div
                className="
                  h-full
                  bg-gradient-to-r
                  from-emerald-400
                  to-teal-300
                  rounded-full
                  transition-all
                  duration-700
                "
                style={{
                  width: `${Math.min(
                    100,
                    Math.max(
                      0,
                      (ocrContribution / 10) * 100
                    )
                  )}%`,
                }}
              />

            </div>

            <div className="text-[10px] text-slate-600 mt-1">
              Weight: 10%
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}