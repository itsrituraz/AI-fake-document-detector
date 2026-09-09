import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  Camera,
  User,
  FileText,
  RefreshCw,
  X,
  ShieldCheck,
} from 'lucide-react';

export default function UploadZone({
  onScreen,
  isLoading,
  presets,
  onSelectPreset,
  activePreset,
}) {
  const [docFile, setDocFile] = useState(null);
  const [docPreview, setDocPreview] = useState(null);
  const [selfieFile, setSelfieFile] = useState(null);
  const [selfiePreview, setSelfiePreview] = useState(null);
  const [docTypeHint, setDocTypeHint] = useState('auto');

  // Webcam capture state
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const docInputRef = useRef(null);
  const selfieInputRef = useRef(null);

  const handleDocChange = (e) => {
    const file = e.target.files?.[0];

    if (file) {
      setDocFile(file);
      setDocPreview(URL.createObjectURL(file));
    }
  };

  const handleSelfieChange = (e) => {
    const file = e.target.files?.[0];

    if (file) {
      setSelfieFile(file);
      setSelfiePreview(URL.createObjectURL(file));
    }
  };

  // Start webcam
  const startCamera = async () => {
    try {
      setIsCameraActive(true);

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 480,
          height: 480,
        },
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      alert(
        'Could not access camera. Please select a selfie image file instead.'
      );

      setIsCameraActive(false);
    }
  };

  // Capture photo from webcam
  const captureCamera = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');

      canvas.width = videoRef.current.videoWidth || 480;
      canvas.height = videoRef.current.videoHeight || 480;

      const ctx = canvas.getContext('2d');

      ctx.drawImage(
        videoRef.current,
        0,
        0,
        canvas.width,
        canvas.height
      );

      canvas.toBlob(
        (blob) => {
          if (blob) {
            const file = new File(
              [blob],
              'selfie_camera_capture.jpg',
              {
                type: 'image/jpeg',
              }
            );

            setSelfieFile(file);
            setSelfiePreview(URL.createObjectURL(blob));
          }

          stopCamera();
        },
        'image/jpeg',
        0.95
      );
    }
  };

  // Stop webcam
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current
        .getTracks()
        .forEach((track) => track.stop());

      streamRef.current = null;
    }

    setIsCameraActive(false);
  };

  // Submit document + selfie for screening
  const handleSubmit = (e) => {
    e.preventDefault();

    if (!docFile) {
      alert('Please upload or select a travel document to screen.');
      return;
    }

    onScreen({
      docFile,
      selfieFile,
      docTypeHint:
        docTypeHint === 'auto' ? null : docTypeHint,
    });
  };

  return (
    <div
      className="
        glass-panel
        rounded-2xl
        p-6 lg:p-8
        mb-8
        border border-teal-500/15
        shadow-[0_0_45px_rgba(20,184,166,0.08)]
      "
    >

      {/* ========================================================= */}
      {/* HEADER + DEMO PRESETS */}
      {/* ========================================================= */}

      <div
        className="
          flex flex-col md:flex-row
          md:items-center
          justify-between
          gap-3
          pb-5
          border-b border-slate-800/80
          mb-6
        "
      >

        {/* Section heading */}
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <UploadCloud className="w-5 h-5 text-teal-400" />

            Document & Biometric Ingestion
          </h2>

          <p className="text-xs text-slate-400 mt-1">
            Select an ID document and optional live selfie portrait
            for comprehensive screening.
          </p>
        </div>

        {/* Demo preset buttons */}
        <div className="flex flex-wrap items-center gap-2">

          <span className="text-xs text-slate-400 font-medium mr-1">
            Demo Presets:
          </span>

          {presets?.map((p) => {
            const isAuth = p.expected_risk === 'LOW';
            const isCrit = p.expected_risk === 'CRITICAL';
            const isSelected = activePreset === p.file;

            return (
              <button
                key={p.file}
                type="button"
                onClick={() => onSelectPreset(p.file)}
                title={p.label}
                className={`
                  text-xs
                  px-3
                  py-1.5
                  rounded-lg
                  font-medium
                  transition-all
                  duration-200
                  border

                  ${
                    isSelected
                      ? `
                        ring-2
                        ring-teal-400
                        bg-teal-950
                        text-teal-200
                        border-teal-500/60
                        shadow-lg
                        shadow-teal-500/10
                      `
                      : isCrit
                      ? `
                        bg-red-950/40
                        text-red-300
                        border-red-800/50
                        hover:bg-red-900/60
                      `
                      : isAuth
                      ? `
                        bg-emerald-950/40
                        text-emerald-300
                        border-emerald-800/50
                        hover:bg-emerald-900/60
                      `
                      : `
                        bg-amber-950/40
                        text-amber-300
                        border-amber-800/50
                        hover:bg-amber-900/60
                      `
                  }
                `}
              >
                {p.type === 'passport' ? '🛂 ' : '📑 '}

                {p.label.split('(')[0].trim()}
              </button>
            );
          })}
        </div>
      </div>


      {/* ========================================================= */}
      {/* MAIN FORM */}
      {/* ========================================================= */}

      <form
        onSubmit={handleSubmit}
        className="space-y-5"
      >

        <div className="grid grid-cols-1 md:grid-cols-12 gap-5">


          {/* ===================================================== */}
          {/* DOCUMENT UPLOAD */}
          {/* ===================================================== */}

          <div className="md:col-span-8 flex flex-col">

            <div className="flex items-center justify-between mb-2">

              <label
                className="
                  text-xs
                  font-semibold
                  text-slate-300
                  flex
                  items-center
                  gap-1.5
                "
              >
                <FileText className="w-4 h-4 text-teal-400" />

                PRIMARY TRAVEL DOCUMENT
                (PASSPORT / VISA / ID)
              </label>


              {/* Document type selector */}
              <div className="flex items-center gap-2">

                <span className="text-xs text-slate-400">
                  Class:
                </span>

                <select
                  value={docTypeHint}
                  onChange={(e) =>
                    setDocTypeHint(e.target.value)
                  }
                  className="
                    text-xs
                    bg-slate-900
                    border border-slate-700
                    text-slate-200
                    rounded
                    px-2
                    py-0.5
                    focus:outline-none
                    focus:ring-1
                    focus:ring-teal-500
                  "
                >
                  <option value="auto">
                    Auto-Detect
                  </option>

                  <option value="passport">
                    Passport (TD3)
                  </option>

                  <option value="visa">
                    Visa (MRV)
                  </option>

                  <option value="national_id">
                    National ID (TD1)
                  </option>

                  <option value="driving_license">
                    Driving License
                  </option>
                </select>

              </div>
            </div>


            {/* Document Drop Zone */}
            <div
              onClick={() =>
                docInputRef.current?.click()
              }
              className={`
                relative
                flex-1
                min-h-[170px]
                border-2
                border-dashed
                rounded-xl
                flex
                flex-col
                items-center
                justify-center
                p-4
                text-center
                cursor-pointer
                transition-all
                duration-300
                overflow-hidden

                ${
                  docPreview
                    ? `
                      border-teal-500/60
                      bg-slate-900/60
                      shadow-lg
                      shadow-teal-500/5
                    `
                    : `
                      border-slate-700
                      hover:border-teal-400/80
                      bg-slate-900/40
                      hover:bg-slate-900/80
                    `
                }
              `}
            >

              <input
                ref={docInputRef}
                type="file"
                accept="image/jpeg,image/png,application/pdf"
                onChange={handleDocChange}
                className="hidden"
              />


              {/* Document preview */}
              {docPreview ? (

                <div className="relative w-full h-full flex flex-col items-center justify-center">

                  <img
                    src={docPreview}
                    alt="Document preview"
                    className="
                      max-h-[160px]
                      object-contain
                      rounded-lg
                      shadow-md
                    "
                  />

                  <div
                    className="
                      absolute
                      inset-0
                      bg-slate-950/60
                      opacity-0
                      hover:opacity-100
                      transition-opacity
                      flex
                      items-center
                      justify-center
                      gap-2
                      text-xs
                      text-teal-300
                      font-medium
                    "
                  >
                    <RefreshCw className="w-4 h-4" />

                    Click to Change Document
                  </div>

                </div>

              ) : (

                /* Empty document state */
                <div className="space-y-2">

                  <div
                    className="
                      w-12
                      h-12
                      rounded-full
                      bg-teal-950/80
                      border
                      border-teal-700/50
                      flex
                      items-center
                      justify-center
                      mx-auto
                      text-teal-400
                      shadow-lg
                      shadow-teal-500/10
                    "
                  >
                    <FileText className="w-6 h-6" />
                  </div>

                  <p className="text-sm font-medium text-slate-200">
                    Drag and drop travel document image or PDF
                  </p>

                  <p className="text-xs text-slate-400">
                    Supports JPG, PNG, PDF
                    (Passport, Visa, National ID, Permits)
                  </p>

                </div>
              )}

            </div>
          </div>


          {/* ===================================================== */}
          {/* SELFIE / BIOMETRIC */}
          {/* ===================================================== */}

          <div className="md:col-span-4 flex flex-col">

            <div className="flex items-center justify-between mb-2">

              <label
                className="
                  text-xs
                  font-semibold
                  text-slate-300
                  flex
                  items-center
                  gap-1.5
                "
              >
                <User className="w-4 h-4 text-teal-400" />

                LIVE / SELFIE PORTRAIT
                (OPTIONAL)
              </label>


              {/* Webcam */}
              {!isCameraActive && (
                <button
                  type="button"
                  onClick={startCamera}
                  className="
                    text-xs
                    text-teal-400
                    hover:text-teal-300
                    flex
                    items-center
                    gap-1
                    font-medium
                    transition-colors
                  "
                >
                  <Camera className="w-3.5 h-3.5" />

                  Webcam
                </button>
              )}

            </div>


            {/* Selfie container */}
            <div
              className="
                relative
                flex-1
                min-h-[170px]
                border-2
                border-dashed
                border-slate-700
                rounded-xl
                bg-slate-900/40
                hover:border-teal-500/50
                transition-all
                duration-300
                p-3
                flex
                flex-col
                items-center
                justify-center
                text-center
                overflow-hidden
              "
            >

              <input
                ref={selfieInputRef}
                type="file"
                accept="image/jpeg,image/png"
                onChange={handleSelfieChange}
                className="hidden"
              />


              {/* Webcam active */}
              {isCameraActive ? (

                <div className="relative w-full h-full flex flex-col items-center justify-center">

                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    className="
                      w-full
                      h-[140px]
                      object-cover
                      rounded-lg
                      border
                      border-teal-500/30
                    "
                  />

                  <div className="flex gap-2 mt-2">

                    {/* Capture */}
                    <button
                      type="button"
                      onClick={captureCamera}
                      className="
                        px-3
                        py-1
                        rounded
                        text-xs
                        font-medium
                        text-white
                        bg-gradient-to-r
                        from-teal-500
                        to-emerald-600
                        hover:from-teal-400
                        hover:to-emerald-500
                        shadow-lg
                        shadow-teal-500/20
                        transition-all
                      "
                    >
                      Capture Photo
                    </button>


                    {/* Cancel */}
                    <button
                      type="button"
                      onClick={stopCamera}
                      className="
                        px-2
                        py-1
                        bg-slate-800
                        hover:bg-slate-700
                        text-slate-300
                        rounded
                        text-xs
                      "
                    >
                      Cancel
                    </button>

                  </div>

                </div>


              ) : selfiePreview ? (

                /* Selfie preview */
                <div className="relative w-full h-full flex flex-col items-center justify-center">

                  <img
                    src={selfiePreview}
                    alt="Selfie preview"
                    className="
                      max-h-[140px]
                      max-w-[140px]
                      object-cover
                      rounded-full
                      border-2
                      border-teal-500/60
                      shadow-lg
                      shadow-teal-500/10
                    "
                  />


                  {/* Remove selfie */}
                  <button
                    type="button"
                    onClick={() => {
                      setSelfieFile(null);
                      setSelfiePreview(null);
                    }}
                    className="
                      absolute
                      top-1
                      right-1
                      p-1
                      bg-slate-900/80
                      rounded-full
                      text-slate-400
                      hover:text-red-400
                      transition-colors
                    "
                  >
                    <X className="w-4 h-4" />
                  </button>

                </div>


              ) : (

                /* Empty selfie state */
                <div
                  onClick={() =>
                    selfieInputRef.current?.click()
                  }
                  className="cursor-pointer space-y-2"
                >

                  <div
                    className="
                      w-10
                      h-10
                      rounded-full
                      bg-teal-950/70
                      border
                      border-teal-800/50
                      flex
                      items-center
                      justify-center
                      mx-auto
                      text-teal-300
                    "
                  >
                    <Camera className="w-5 h-5" />
                  </div>

                  <p className="text-xs font-medium text-slate-300">
                    Upload selfie or click webcam
                  </p>

                  <p className="text-[11px] text-slate-500">
                    For 1:1 facial biometric matching
                  </p>

                </div>
              )}

            </div>
          </div>

        </div>


        {/* ========================================================= */}
        {/* ACTION BAR */}
        {/* ========================================================= */}

        <div
          className="
            flex
            flex-col
            sm:flex-row
            sm:items-center
            sm:justify-between
            gap-4
            pt-2
          "
        >

          {/* Engine status */}
          <div className="text-xs text-slate-400 flex items-center gap-2">

            <span
              className="
                inline-block
                w-2
                h-2
                rounded-full
                bg-emerald-400
                shadow-[0_0_8px_rgba(52,211,153,0.8)]
              "
            />

            All 4 Inspection Engines Ready:
            OCR • Checksums • Multi-Forensics • Biometrics

          </div>


          {/* Main action */}
          <button
            type="submit"
            disabled={isLoading || !docFile}
            className={`
              px-6
              py-2.5
              rounded-xl
              font-semibold
              text-sm
              flex
              items-center
              justify-center
              gap-2.5
              transition-all
              duration-300
              shadow-lg

              ${
                isLoading || !docFile
                  ? `
                    bg-slate-800
                    text-slate-500
                    cursor-not-allowed
                  `
                  : `
                    bg-gradient-to-r
                    from-teal-500
                    via-emerald-500
                    to-cyan-500

                    hover:from-teal-400
                    hover:via-emerald-400
                    hover:to-cyan-400

                    text-white

                    shadow-teal-500/25

                    hover:shadow-teal-500/40

                    cursor-pointer

                    active:scale-[0.98]
                  `
              }
            `}
          >

            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-white" />

                Executing Screening Pipeline...
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />

                Screen Document & Verify
              </>
            )}

          </button>

        </div>

      </form>
    </div>
  );
}