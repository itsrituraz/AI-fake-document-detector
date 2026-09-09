import React, { useState } from 'react';
import {
  Eye,
  Square,
  Shield,
  User,
  Flame,
} from 'lucide-react';

export default function DocumentViewer({
  docPreviewUrl,
  elaHeatmapUrl,
  ocrBoxes,
  faceBbox,
  stampBbox,
  docDimensions,
}) {
  const [showOcrBoxes, setShowOcrBoxes] = useState(false);
  const [showElaHeatmap, setShowElaHeatmap] = useState(false);
  const [showFaceBox, setShowFaceBox] = useState(true);
  const [showStampBox, setShowStampBox] = useState(true);

  if (!docPreviewUrl) return null;

  // Original document dimensions
  const origW = docDimensions?.width || 900;
  const origH = docDimensions?.height || 600;

  return (
    <div
      className="
        glass-panel
        rounded-2xl
        p-5
        lg:p-6
        mb-8
        border border-teal-500/10
        bg-slate-950/25
        shadow-[0_0_45px_rgba(20,184,166,0.035)]
      "
    >
      {/* ===================================================== */}
      {/* HEADER */}
      {/* ===================================================== */}

      <div
        className="
          flex
          flex-wrap
          items-center
          justify-between
          gap-3
          pb-3
          border-b
          border-slate-800/80
          mb-4
        "
      >
        <div className="flex items-center gap-2">
          <div
            className="
              w-7
              h-7
              rounded-lg
              bg-teal-950/70
              border border-teal-800/50
              flex items-center justify-center
            "
          >
            <Eye className="w-4 h-4 text-teal-400" />
          </div>

          <div>
            <h3
              className="
                text-xs
                font-bold
                uppercase
                tracking-[0.14em]
                text-slate-200
              "
            >
              Interactive Forensic Visual Inspector
            </h3>

            <p className="text-[10px] text-slate-500 mt-0.5">
              Visual evidence & forensic overlay analysis
            </p>
          </div>
        </div>

        {/* ================================================= */}
        {/* OVERLAY CONTROLS */}
        {/* ================================================= */}

        <div className="flex flex-wrap items-center gap-2">

          {/* ELA */}
          <button
            type="button"
            onClick={() => setShowElaHeatmap(!showElaHeatmap)}
            className={`
              text-xs
              px-2.5
              py-1.5
              rounded-md
              font-medium
              flex
              items-center
              gap-1.5
              transition-all
              duration-200
              border

              ${
                showElaHeatmap
                  ? `
                    bg-amber-500
                    text-slate-950
                    border-amber-400
                    font-bold
                    shadow-md
                    shadow-amber-500/20
                  `
                  : `
                    bg-slate-900/80
                    text-slate-300
                    border-slate-700
                    hover:border-amber-500/40
                    hover:text-amber-300
                  `
              }
            `}
          >
            <Flame className="w-3.5 h-3.5" />
            ELA Heatmap
          </button>


          {/* OCR */}
          <button
            type="button"
            onClick={() => setShowOcrBoxes(!showOcrBoxes)}
            className={`
              text-xs
              px-2.5
              py-1.5
              rounded-md
              font-medium
              flex
              items-center
              gap-1.5
              transition-all
              duration-200
              border

              ${
                showOcrBoxes
                  ? `
                    bg-teal-500
                    text-slate-950
                    border-teal-400
                    font-bold
                    shadow-md
                    shadow-teal-500/20
                  `
                  : `
                    bg-slate-900/80
                    text-slate-300
                    border-slate-700
                    hover:border-teal-500/40
                    hover:text-teal-300
                  `
              }
            `}
          >
            <Square className="w-3.5 h-3.5" />
            OCR Boxes
          </button>


          {/* FACE */}
          <button
            type="button"
            onClick={() => setShowFaceBox(!showFaceBox)}
            className={`
              text-xs
              px-2.5
              py-1.5
              rounded-md
              font-medium
              flex
              items-center
              gap-1.5
              transition-all
              duration-200
              border

              ${
                showFaceBox
                  ? `
                    bg-cyan-500
                    text-slate-950
                    border-cyan-400
                    font-bold
                    shadow-md
                    shadow-cyan-500/20
                  `
                  : `
                    bg-slate-900/80
                    text-slate-300
                    border-slate-700
                    hover:border-cyan-500/40
                    hover:text-cyan-300
                  `
              }
            `}
          >
            <User className="w-3.5 h-3.5" />
            Face Crop
          </button>


          {/* SEAL */}
          <button
            type="button"
            onClick={() => setShowStampBox(!showStampBox)}
            className={`
              text-xs
              px-2.5
              py-1.5
              rounded-md
              font-medium
              flex
              items-center
              gap-1.5
              transition-all
              duration-200
              border

              ${
                showStampBox
                  ? `
                    bg-emerald-500
                    text-slate-950
                    border-emerald-400
                    font-bold
                    shadow-md
                    shadow-emerald-500/20
                  `
                  : `
                    bg-slate-900/80
                    text-slate-300
                    border-slate-700
                    hover:border-emerald-500/40
                    hover:text-emerald-300
                  `
              }
            `}
          >
            <Shield className="w-3.5 h-3.5" />
            Seal Region
          </button>

        </div>
      </div>


      {/* ===================================================== */}
      {/* IMAGE CANVAS */}
      {/* ===================================================== */}

      <div
        className="
          relative
          w-full
          max-h-[480px]
          bg-[#050912]
          rounded-xl
          overflow-hidden
          flex
          items-center
          justify-center
          p-2
          border
          border-teal-500/10
          shadow-inner
        "
      >

        {/* Top status strip */}
        <div
          className="
            absolute
            top-2
            left-3
            z-10
            flex
            items-center
            gap-1.5
            px-2
            py-1
            rounded-md
            bg-slate-950/70
            border border-slate-700/70
            backdrop-blur-sm
          "
        >
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_7px_rgba(52,211,153,0.8)]" />

          <span className="text-[10px] text-slate-300 font-mono">
            {showElaHeatmap
              ? 'ELA / ANALYSIS MODE'
              : 'NATURAL / SOURCE MODE'}
          </span>
        </div>


        {/* ================================================= */}
        {/* BASE IMAGE */}
        {/* ================================================= */}

        <img
          src={
            showElaHeatmap && elaHeatmapUrl
              ? elaHeatmapUrl
              : docPreviewUrl
          }
          alt="Document inspection target"
          className="
            max-h-[460px]
            w-auto
            object-contain
            rounded-lg
            shadow-[0_0_30px_rgba(0,0,0,0.45)]
            transition-all
            duration-300
          "
        />


        {/* ================================================= */}
        {/* SVG FORENSIC OVERLAYS */}
        {/* ================================================= */}

        <svg
          className="
            absolute
            inset-0
            w-full
            h-full
            pointer-events-none
          "
          viewBox={`0 0 ${origW} ${origH}`}
          preserveAspectRatio="xMidYMid meet"
        >

          {/* ================================================= */}
          {/* OCR BOXES */}
          {/* ================================================= */}

          {showOcrBoxes &&
            ocrBoxes?.map((b, idx) => (
              <rect
                key={idx}
                x={b.bbox.x}
                y={b.bbox.y}
                width={b.bbox.w}
                height={b.bbox.h}
                fill="rgba(20, 184, 166, 0.12)"
                stroke="#2dd4bf"
                strokeWidth="1.5"
              />
            ))}


          {/* ================================================= */}
          {/* FACE BOX */}
          {/* ================================================= */}

          {showFaceBox && faceBbox && (
            <g>
              <rect
                x={faceBbox.x}
                y={faceBbox.y}
                width={faceBbox.w}
                height={faceBbox.h}
                fill="rgba(6, 182, 212, 0.12)"
                stroke="#22d3ee"
                strokeWidth="2.5"
                strokeDasharray="4 2"
              />

              <text
                x={faceBbox.x + 4}
                y={faceBbox.y - 6}
                fill="#67e8f9"
                fontSize="14"
                fontWeight="bold"
              >
                BIOMETRIC PORTRAIT
              </text>
            </g>
          )}


          {/* ================================================= */}
          {/* SEAL BOX */}
          {/* ================================================= */}

          {showStampBox && stampBbox && (
            <g>
              <rect
                x={stampBbox.x}
                y={stampBbox.y}
                width={stampBbox.w}
                height={stampBbox.h}
                fill="rgba(16, 185, 129, 0.10)"
                stroke="#34d399"
                strokeWidth="2.5"
              />

              <text
                x={stampBbox.x + 4}
                y={stampBbox.y - 6}
                fill="#6ee7b7"
                fontSize="14"
                fontWeight="bold"
              >
                CONSULAR SEAL
              </text>
            </g>
          )}

        </svg>

      </div>


      {/* ===================================================== */}
      {/* LEGEND / FOOTER */}
      {/* ===================================================== */}

      <div
        className="
          flex
          flex-wrap
          items-center
          justify-between
          gap-2
          text-[11px]
          text-slate-400
          mt-3
          px-1
        "
      >

        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />

          Active Layer:
          <span className="text-slate-300">
            {showElaHeatmap
              ? 'ELA Heatmap'
              : 'Natural Spectrum'}
          </span>
        </span>

        <span className="font-mono text-slate-500">
          DOCUMENT SIZE: {origW} × {origH} PX
        </span>

      </div>

    </div>
  );
}