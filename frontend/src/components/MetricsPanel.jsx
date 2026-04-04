import React, { useEffect, useState } from 'react';

export default function MetricsPanel({ data, isProcessing }) {
  const [animated, setAnimated] = useState({
    total_detections: 0,
    enemy_count: 0,
    vehicle_count: 0,
    fps: 0,
    duration: 0,
  });

  useEffect(() => {
    if (!data) return;
    // Count-up animation
    const targets = {
      total_detections: data.total_detections || 0,
      enemy_count: data.enemy_count || 0,
      vehicle_count: data.vehicle_count || 0,
      fps: data.fps || 0,
      duration: data.duration || 0,
    };

    const steps = 40;
    let step = 0;
    const interval = setInterval(() => {
      step++;
      const t = step / steps;
      const ease = 1 - Math.pow(1 - t, 3);
      setAnimated({
        total_detections: Math.round(targets.total_detections * ease),
        enemy_count: Math.round(targets.enemy_count * ease),
        vehicle_count: Math.round(targets.vehicle_count * ease),
        fps: +(targets.fps * ease).toFixed(1),
        duration: +(targets.duration * ease).toFixed(1),
      });
      if (step >= steps) clearInterval(interval);
    }, 30);

    return () => clearInterval(interval);
  }, [data]);

  const threatLevel = data?.threat_level || 'LOW';
  const resolution = data?.resolution || '—';
  const frameCount = data?.frame_count || 0;

  const threatConfig = {
    HIGH:   { color: 'var(--c-red)',    icon: '🔴', label: 'CRITICAL THREAT', dotClass: 'red' },
    MEDIUM: { color: 'var(--c-yellow)', icon: '🟡', label: 'MODERATE THREAT',  dotClass: 'yellow' },
    LOW:    { color: 'var(--c-green)',  icon: '🟢', label: 'MINIMAL THREAT',    dotClass: '' },
  };

  const tc = threatConfig[threatLevel] || threatConfig.LOW;

  const stats = [
    { icon: '🎯', value: animated.total_detections, label: 'TOTAL DETECTIONS' },
    { icon: '👤', value: animated.enemy_count,       label: 'ENEMY SOLDIERS',   color: 'var(--c-red)' },
    { icon: '🚗', value: animated.vehicle_count,     label: 'MIL VEHICLES',      color: 'var(--c-yellow)' },
    { icon: '⚡', value: animated.fps,               label: 'PROC FPS' },
    { icon: '⏱', value: `${animated.duration}s`,    label: 'DURATION' },
    { icon: '📹', value: resolution,                 label: 'RESOLUTION' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', height: '100%' }}>
      {/* Threat Level Card */}
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title">⚠ Threat Assessment</span>
          {data && <span className="panel-badge">{frameCount} FRAMES</span>}
        </div>
        <div className="threat-card">
          <div className="threat-label">THREAT LEVEL</div>
          <div
            className={`threat-value ${threatLevel}`}
            style={{ color: tc.color }}
          >
            {isProcessing ? '...' : threatLevel}
          </div>
          <div className="threat-indicator" style={{ color: tc.color }}>
            <span className={`dot ${tc.dotClass}`} />
            {isProcessing ? 'ANALYZING...' : (data ? tc.label : 'AWAITING INPUT')}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="panel" style={{ flex: 1 }}>
        <div className="panel-header">
          <span className="panel-title">📊 Mission Metrics</span>
          {isProcessing && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{
                width: 6, height: 6, borderRadius: '50%',
                background: 'var(--c-green)',
                animation: 'blink 0.8s ease-in-out infinite'
              }} />
              <span className="panel-badge">LIVE</span>
            </div>
          )}
        </div>
        <div className="stats-grid">
          {stats.map((s, i) => (
            <div key={i} className="stat-cell">
              <div className="stat-icon">{s.icon}</div>
              <div className="stat-value" style={s.color ? { color: s.color } : {}}>
                {isProcessing && typeof s.value === 'number' ? '---' : s.value}
              </div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
