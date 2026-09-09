import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import UploadZone from './components/UploadZone';
import RiskGauge from './components/RiskGauge';
import DocumentViewer from './components/DocumentViewer';
import ForensicsCard from './components/ForensicsCard';
import BiometricsCard from './components/BiometricsCard';
import ValidationCard from './components/ValidationCard';
import OcrCard from './components/OcrCard';
import OfficerDecisionConsole from './components/OfficerDecisionConsole';
import HistoryModal from './components/HistoryModal';
import { ShieldCheck, Sparkles, RefreshCw } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [report, setReport] = useState(null);
  const [docPreviewUrl, setDocPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [presets, setPresets] = useState([]);
  const [activePreset, setActivePreset] = useState(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Fetch pre-generated demo specimen presets on load
  useEffect(() => {
    fetch(`${API_URL}/api/specimens`)
      .then((res) => res.json())
      .then((data) => {
        if (data.specimens) setPresets(data.specimens);
      })
      .catch((err) => console.error('Could not load presets:', err));
  }, []);

  // Execute screening against FastAPI backend
  const handleScreen = async ({ docFile, selfieFile, docTypeHint }) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('document', docFile);
      if (selfieFile) {
        formData.append('selfie', selfieFile);
      }
      if (docTypeHint) {
        formData.append('document_type', docTypeHint);
      }

      // Preview URL for the visual inspector
      setDocPreviewUrl(URL.createObjectURL(docFile));

      const res = await fetch(`${API_URL}/api/screen`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Screening server error');
      }

      const data = await res.json();
      setReport(data);
    } catch (err) {
      alert('Screening execution failed: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // 1-Click Demo Preset Loader
  const handleSelectPreset = async (fileName) => {
    if (!fileName) return;
    setActivePreset(fileName);
    const presetMeta = presets.find((p) => p.file === fileName);
    if (!presetMeta) return;

    setIsLoading(true);
    try {
      // 1. Fetch document blob
      const docRes = await fetch(`${API_URL}/static/specimens/${presetMeta.file}`);
      const docBlob = await docRes.blob();
      const docFile = new File([docBlob], presetMeta.file, { type: 'image/jpeg' });

      // 2. Fetch matching selfie blob if defined
      let selfieFile = null;
      if (presetMeta.matching_selfie) {
        const selfieRes = await fetch(`${API_URL}/static/specimens/${presetMeta.matching_selfie}`);
        const selfieBlob = await selfieRes.blob();
        selfieFile = new File([selfieBlob], presetMeta.matching_selfie, { type: 'image/jpeg' });
      }

      // 3. Immediately trigger screening
      await handleScreen({
        docFile,
        selfieFile,
        docTypeHint: presetMeta.type
      });
    } catch (err) {
      alert('Failed to load specimen preset: ' + err.message);
      setIsLoading(false);
    }
  };

  return (
   <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col selection:bg-cyan-400 selection:text-slate-950">
      
      {/* Navigation & Header */}
      <Navbar
        onOpenHistory={() => setIsHistoryOpen(true)}
        presets={presets}
        activePreset={activePreset}
        onSelectPreset={handleSelectPreset}
      />

      {/* Hero Banner */}
      <Hero />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6">
        
        {/* Upload & Ingestion Section */}
        <UploadZone
          onScreen={handleScreen}
          isLoading={isLoading}
          presets={presets}
          activePreset={activePreset}
          onSelectPreset={handleSelectPreset}
        />

        {/* Loading Spinner State */}
        {isLoading && (
          <div className="glass-panel rounded-2xl p-12 text-center my-6 flex flex-col items-center justify-center space-y-4 border border-cyan-500/30">
            <div className="relative">
              <RefreshCw className="w-10 h-10 animate-spin text-cyan-400" />
              <ShieldCheck className="w-5 h-5 text-emerald-400 absolute top-2.5 left-2.5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-bold text-white">
                Multi-Signal AI Inspection in Progress
              </h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Extracting OCR text &bull; Computing ICAO 9303 checksums &bull; Performing Error Level Analysis &bull; Verifying face biometric embeddings
              </p>
            </div>
          </div>
        )}

        {/* Screening Results Dashboard */}
        {report && !isLoading && (
          <div className="space-y-8 animate-fade-in">
            
            {/* 1. Executive Risk Gauge & Recommendation */}
            <RiskGauge assessment={report.risk_assessment} />

            {/* 2. Interactive Forensic Visual Inspector */}
            <DocumentViewer
              docPreviewUrl={docPreviewUrl}
              elaHeatmapUrl={report.forensics?.ela_heatmap_base64}
              ocrBoxes={report.ocr?.ocr_boxes}
              faceBbox={report.biometrics?.document_face_bbox}
              stampBbox={report.forensics?.stamp_details?.stamp_bbox}
              docDimensions={report.document_summary?.dimensions}
            />

            {/* 3. Deep Dive Two-Column Technical Matrix */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Left Column: Forensics & Biometrics */}
              <div className="space-y-6">
                <ForensicsCard forensics={report.forensics} />
                <BiometricsCard biometrics={report.biometrics} />
              </div>

              {/* Right Column: Validation Rules & OCR Fields */}
              <div className="space-y-6">
                <ValidationCard validation={report.validation} />
                <OcrCard ocr={report.ocr} />
              </div>

            </div>

            {/* 4. Human Officer Decision Console */}
            <OfficerDecisionConsole
              screeningId={report.screening_id}
              onDecisionRecorded={(dec) => {
                console.log('Officer verdict recorded:', dec);
              }}
            />

          </div>
        )}

      </main>

      {/* Audit History Modal */}
      <HistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onLoadScreening={(savedReport) => {
          setReport(savedReport);
          setActivePreset(null);
        }}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950/60 py-4 px-4 text-center">
  <div className="text-xs font-semibold tracking-wider text-teal-400">
    TEAM WILDCARD
  </div>

  <div className="text-[10px] text-slate-500 mt-1">
    BORDER SENTRY &bull; AI-Powered Identity Verification
  </div>
</footer>

    </div>
  );
}
