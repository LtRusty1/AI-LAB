import React, { useState, useEffect } from 'react';
import './PerformanceMonitor.css';

const PerformanceMonitor = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);

  useEffect(() => {
    fetchMetrics();
    
    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8001/metrics');
      const data = await response.json();
      setMetrics(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
      setLoading(false);
    }
  };

  const runBenchmark = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8001/benchmark/llm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const result = await response.json();
      alert(`Benchmark Results:\nAverage Time: ${result.avg_time?.toFixed(2)}s\nTotal Time: ${result.total_time?.toFixed(2)}s\nIterations: ${result.iterations}`);
    } catch (error) {
      alert(`Benchmark failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (value, thresholds) => {
    if (value > thresholds.danger) return '#ef4444';
    if (value > thresholds.warning) return '#f59e0b';
    return '#10b981';
  };

  if (loading && !metrics) {
    return (
      <div className="performance-monitor">
        <h3>Performance Monitor</h3>
        <div className="loading">Loading metrics...</div>
      </div>
    );
  }

  return (
    <div className="performance-monitor">
      <div className="monitor-header">
        <h3>System Performance</h3>
        <div className="controls">
          <label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          {autoRefresh && (
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
            >
              <option value={1000}>1s</option>
              <option value={5000}>5s</option>
              <option value={10000}>10s</option>
              <option value={30000}>30s</option>
            </select>
          )}
          <button onClick={fetchMetrics} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
          <button onClick={runBenchmark} disabled={loading}>
            Run Benchmark
          </button>
        </div>
      </div>

      {metrics && (
        <div className="metrics-grid">
          <div className="metric-card">
            <h4>CPU Usage</h4>
            <div className="metric-value">
              <span 
                style={{ color: getStatusColor(metrics.cpu_usage_percent, { warning: 70, danger: 90 }) }}
              >
                {metrics.cpu_usage_percent?.toFixed(1)}%
              </span>
            </div>
            <div className="metric-bar">
              <div 
                className="metric-fill" 
                style={{ 
                  width: `${metrics.cpu_usage_percent}%`,
                  backgroundColor: getStatusColor(metrics.cpu_usage_percent, { warning: 70, danger: 90 })
                }}
              />
            </div>
          </div>

          <div className="metric-card">
            <h4>Memory Usage</h4>
            <div className="metric-value">
              <span 
                style={{ color: getStatusColor(metrics.memory_usage_percent, { warning: 80, danger: 95 }) }}
              >
                {metrics.memory_usage_percent?.toFixed(1)}%
              </span>
            </div>
            <div className="metric-details">
              {formatBytes(metrics.memory_used)} / {formatBytes(metrics.memory_total)}
            </div>
            <div className="metric-bar">
              <div 
                className="metric-fill" 
                style={{ 
                  width: `${metrics.memory_usage_percent}%`,
                  backgroundColor: getStatusColor(metrics.memory_usage_percent, { warning: 80, danger: 95 })
                }}
              />
            </div>
          </div>

          {metrics.gpu_memory_usage_percent !== undefined && (
            <div className="metric-card">
              <h4>GPU Memory</h4>
              <div className="metric-value">
                <span 
                  style={{ color: getStatusColor(metrics.gpu_memory_usage_percent, { warning: 80, danger: 95 }) }}
                >
                  {metrics.gpu_memory_usage_percent?.toFixed(1)}%
                </span>
              </div>
              <div className="metric-details">
                {formatBytes(metrics.gpu_memory_used)} / {formatBytes(metrics.gpu_memory_total)}
              </div>
              <div className="metric-bar">
                <div 
                  className="metric-fill" 
                  style={{ 
                    width: `${metrics.gpu_memory_usage_percent}%`,
                    backgroundColor: getStatusColor(metrics.gpu_memory_usage_percent, { warning: 80, danger: 95 })
                  }}
                />
              </div>
            </div>
          )}

          <div className="metric-card">
            <h4>Disk Usage</h4>
            <div className="metric-value">
              <span 
                style={{ color: getStatusColor(metrics.disk_usage_percent, { warning: 85, danger: 95 }) }}
              >
                {metrics.disk_usage_percent?.toFixed(1)}%
              </span>
            </div>
            <div className="metric-details">
              {formatBytes(metrics.disk_used)} / {formatBytes(metrics.disk_total)}
            </div>
            <div className="metric-bar">
              <div 
                className="metric-fill" 
                style={{ 
                  width: `${metrics.disk_usage_percent}%`,
                  backgroundColor: getStatusColor(metrics.disk_usage_percent, { warning: 85, danger: 95 })
                }}
              />
            </div>
          </div>

          <div className="metric-card info-card">
            <h4>System Info</h4>
            <div className="info-list">
              <div>Uptime: {Math.floor(metrics.uptime / 3600)}h {Math.floor((metrics.uptime % 3600) / 60)}m</div>
              <div>Python Version: {metrics.python_version}</div>
              <div>Platform: {metrics.platform}</div>
              {metrics.gpu_available && <div>GPU: Available</div>}
            </div>
          </div>

          <div className="metric-card info-card">
            <h4>Network</h4>
            <div className="info-list">
              <div>Sent: {formatBytes(metrics.network_sent)}</div>
              <div>Received: {formatBytes(metrics.network_recv)}</div>
            </div>
          </div>
        </div>
      )}

      <div className="timestamp">
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default PerformanceMonitor; 