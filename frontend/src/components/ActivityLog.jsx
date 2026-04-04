import React, { useEffect, useState } from 'react';

export default function ActivityLog({ entries = [] }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    setLogs(entries);
  }, [entries]);

  if (logs.length === 0) return null;

  return (
    <div className="activity-log">
      {logs.slice(-8).reverse().map((entry, i) => (
        <div key={i} className="log-entry">
          <span className="log-time">{entry.time}</span>
          <span className={`log-message ${entry.type || ''}`}>{entry.msg}</span>
        </div>
      ))}
    </div>
  );
}
