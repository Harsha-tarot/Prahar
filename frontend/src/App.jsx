import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import MetricsPanel from './components/MetricsPanel';
import TerrainMap from './components/TerrainMap';
import ActivityLog from './components/ActivityLog';

const API_BASE = 'http://localhost:5000';

function Clock() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <span className="clock">
      {time.toUTCString().slice(17, 25)} UTC
    </span>
  );
}

function formatTime() {
  return new Date().toLocaleTimeString('en-US', { hour12: false });
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [logs, setLogs] = useState([]);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const addLog = useCallback((msg, type = '') => {
    setLogs(prev => [...prev, { time: formatTime(), msg, type }]);
  }, []);

  // Health check
  useEffect(() => {
    const check = async () => {
      try {
        await axios.get(`${API_BASE}/health`, { timeout: 2000 });
        setBackendOnline(true);
        addLog('Backend PRAHAR-EDGE-AI online.', 'success');
      } catch {
        setBackendOnline(false);
        addLog('Backend offline — start python app.py', 'warn');
      }
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleFileSelect = (file) => {
    if (!file) return;
    if (!file.type.startsWith('video/')) {
      setError('Please upload a video file (MP4, AVI, MOV)');
      return;
    }
    setSelectedFile(file);
    setResult(null);
    setError(null);
    addLog(`Video loaded: ${file.name} (${(file.size / 1024 / 1024).toFixed(1)} MB)`);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    // Guard: backend must be reachable before we start a long upload
    if (!backendOnline) {
      setError('Backend is offline. Run: cd prahar/backend && python app.py');
      addLog('Cannot analyze — backend is not running. Start python app.py', 'error');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);
    addLog('Initiating YOLOv8 inference pipeline...', 'success');
    addLog('Uploading video to PRAHAR backend...');

    const formData = new FormData();
    formData.append('video', selectedFile);

    try {
      addLog('Processing frames... (may take a few minutes for large files)', 'warn');
      const res = await axios.post(`${API_BASE}/analyze-video`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 600000, // 10 min timeout
      });

      const data = res.data;
      setResult(data);
      addLog(`Analysis complete! ${data.total_detections} detections found.`, 'success');
      addLog(`Threat Level: ${data.threat_level} | Enemies: ${data.enemy_count} | Vehicles: ${data.vehicle_count}`, data.threat_level === 'HIGH' ? 'error' : 'success');

      // Auto-play the video
      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.load();
          videoRef.current.play().catch(() => {});
        }
      }, 500);
    } catch (err) {
      const msg = err.response?.data?.error || err.message || 'Analysis failed';
      setError(msg);
      addLog(`Error: ${msg}`, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    addLog('System reset. Ready for new mission.');
  };

  const threatLevel = result?.threat_level || 'LOW';
  const isHighThreat = threatLevel === 'HIGH';
  const isMediumThreat = threatLevel === 'MEDIUM';

  const headerBorderColor = isHighThreat
    ? 'var(--c-red)'
    : isMediumThreat
    ? 'var(--c-yellow)'
    : 'var(--c-border2)';

  return (
    <div className="app-container">
      {/* ── Header ── */}
      <header className="header" style={{ borderBottomColor: headerBorderColor }}>
        <div className="header-logo">
          <div className="logo-icon">AI</div>
          <div className="logo-text">
            <h1>PRAHAR</h1>
            <span>Real-Time Edge AI Reconnaissance System</span>
          </div>
        </div>

        <div className="header-status">
          <div className="status-dot">
            <span className={`dot ${backendOnline ? '' : 'offline'}`} />
            {backendOnline ? 'BACKEND ONLINE' : 'BACKEND OFFLINE'}
          </div>
          {result && (
            <div className="status-dot">
              <span className={`dot ${isHighThreat ? 'red' : isMediumThreat ? 'yellow' : ''}`} />
              THREAT: {threatLevel}
            </div>
          )}
          <Clock />
        </div>
      </header>

      {/* ── Main ── */}
      <main className="main-content">

        {/* ── Upload Section ── */}
        <section className="panel upload-section">
          <div className="panel-header">
            <span className="panel-title">🛸 Mission Upload – Drone Footage</span>
            <span className="panel-badge">YOLOv8 · OpenCV</span>
          </div>
          <div style={{ padding: '16px' }}>
            <div
              className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={e => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              role="button"
              aria-label="Upload drone video"
              id="upload-zone"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                className="upload-input"
                id="video-file-input"
                onChange={e => handleFileSelect(e.target.files[0])}
              />
              <div className="upload-icon">🎥</div>
              <div className="upload-text">
                <h3>UPLOAD DRONE FOOTAGE</h3>
                <p>MP4, AVI, MOV · Drag & Drop or Click · Max 500MB</p>
              </div>
            </div>

            {selectedFile && (
              <div className="upload-file-info">
                <span className="file-name">📁 {selectedFile.name}</span>
                <div className="upload-actions">
                  <button
                    id="analyze-btn"
                    className={`btn ${backendOnline ? 'btn-primary' : 'btn-danger'}`}
                    onClick={handleAnalyze}
                    disabled={isProcessing}
                    title={!backendOnline ? 'Backend offline — click for details' : 'Analyze video with YOLOv8'}
                  >
                    {isProcessing ? (
                      <>
                        <div style={{
                          width: 14, height: 14,
                          border: '2px solid rgba(255,255,255,0.3)',
                          borderTopColor: 'white',
                          borderRadius: '50%',
                          animation: 'spin 0.8s linear infinite'
                        }} />
                        ANALYZING...
                      </>
                    ) : backendOnline ? '⚡ ANALYZE' : '⚠ ANALYZE (START BACKEND)'}
                  </button>
                  <button
                    id="reset-btn"
                    className="btn btn-outline"
                    onClick={handleReset}
                    disabled={isProcessing}
                  >
                    ✕ RESET
                  </button>
                </div>
              </div>
            )}

            {error && (
              <div style={{
                marginTop: 12,
                padding: '10px 16px',
                background: 'rgba(255,34,68,0.08)',
                border: '1px solid rgba(255,34,68,0.3)',
                borderRadius: 6,
                fontFamily: 'var(--font-mono)',
                fontSize: '0.75rem',
                color: 'var(--c-red)',
              }}>
                ⚠ ERROR: {error}
              </div>
            )}

            <ActivityLog entries={logs} />
          </div>
        </section>

        {/* ── Video Panel ── */}
        <section className="panel video-panel">
          <div className="panel-header">
            <span className="panel-title">📡 Reconnaissance Feed – Processed Output</span>
            {result && (
              <span className="panel-badge">{result.resolution} · {result.fps} FPS</span>
            )}
          </div>
          <div className="video-container">
            {/* Scan line */}
            {isProcessing && <div className="scan-line" />}

            {/* High threat flashing border */}
            {result && isHighThreat && (
              <>
                <div className="threat-alert-overlay" />
                <div className="threat-banner">⚠ HIGH THREAT DETECTED ⚠</div>
              </>
            )}

            {/* Medium threat border */}
            {result && isMediumThreat && (
              <div style={{
                position: 'absolute', inset: 0, pointerEvents: 'none',
                border: '2px solid var(--c-yellow)', zIndex: 10
              }} />
            )}

            {/* Processing overlay */}
            {isProcessing && (
              <div className="processing-overlay">
                <div className="processing-spinner" />
                <div className="processing-text">PRAHAR ANALYZING FOOTAGE</div>
                <div className="processing-subtext">Running YOLOv8 · Frame-by-Frame Inference</div>
                <div className="processing-subtext">This may take 1–3 minutes depending on video length...</div>
              </div>
            )}

            {/* Processed video */}
            {result?.video_url ? (
              <video
                ref={videoRef}
                id="processed-video"
                className="analyzed-video"
                src={`${API_BASE}${result.video_url}`}
                controls
                loop
                autoPlay
                muted
                playsInline
              />
            ) : (
              !isProcessing && (
                <div className="video-placeholder">
                  <span>📡</span>
                  <p>{selectedFile ? 'READY TO ANALYZE' : 'NO FOOTAGE LOADED'}</p>
                  <p style={{ fontSize: '0.6rem', opacity: 0.5, marginTop: 4 }}>
                    Upload a drone video to begin threat detection
                  </p>
                </div>
              )
            )}
          </div>
        </section>

        {/* ── Metrics Panel ── */}
        <div className="metrics-panel">
          <MetricsPanel data={result} isProcessing={isProcessing} />
        </div>

        {/* ── 3D Terrain Map ── */}
        <section className="panel map-section">
          <div className="panel-header">
            <span className="panel-title">🌐 3D Terrain Intelligence Map</span>
            <div className="map-legend">
              <div className="legend-item">
                <div className="legend-dot" style={{ background: '#ff2244' }} />
                Enemy Soldier
              </div>
              <div className="legend-item">
                <div className="legend-dot" style={{ background: '#ffcc00' }} />
                Military Vehicle
              </div>
              <div className="legend-item">
                <div className="legend-dot" style={{ background: '#00ff8c', opacity: 0.4 }} />
                Terrain
              </div>
            </div>
          </div>
          <div className="terrain-container">
            <TerrainMap
              threatCoordinates={result?.threat_coordinates || []}
              threatLevel={threatLevel}
              videoUrl={result?.video_url ? `${API_BASE}${result.video_url}` : null}
            />
            <div style={{
              position: 'absolute',
              bottom: 10,
              right: 12,
              fontFamily: 'var(--font-mono)',
              fontSize: '0.6rem',
              color: 'var(--c-text-dim)',
              pointerEvents: 'none',
            }}>
              THREE.JS · AUTO-ORBIT · {result?.threat_coordinates?.length || 4} MARKERS
            </div>
          </div>
        </section>
      </main>

      {/* ── Footer ── */}
      <footer style={{
        padding: '12px 28px',
        borderTop: '1px solid var(--c-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(5,9,15,0.9)',
      }}>
        <span style={{
          fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--c-text-dim)'
        }}>
          PRAHAR EDGE AI v1.0 · YOLOv8 · OpenCV · Three.js · React
        </span>
        <span style={{
          fontFamily: 'var(--font-mono)', fontSize: '0.65rem', color: 'var(--c-text-dim)'
        }}>
          POWERED BY DATATURE ANNOTATION PIPELINE · ULTRALYTICS YOLOV8
        </span>
      </footer>
    </div>
  );
}
