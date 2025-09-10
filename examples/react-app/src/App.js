import React, { useState, useRef, useEffect } from 'react';
import { embedDashboard } from '@superset-ui/embedded-sdk';
import './App.css';

function App() {
  const [dashboardId, setDashboardId] = useState('b713fcc3-167a-4961-ac21-2fa7e851b514');
  const [supersetUrl, setSupersetUrl] = useState('https://analytics.paycorp.io');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isEmbedded, setIsEmbedded] = useState(false);
  const dashboardRef = useRef(null);

  // Fetch guest token from your backend
  const fetchGuestToken = async () => {
    try {
      const response = await fetch('/generate-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          dashboard: dashboardId,
          rls: [] // Add RLS rules here if needed
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch token: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.token;
    } catch (err) {
      console.error('Error fetching guest token:', err);
      throw err;
    }
  };

  const embedDashboardComponent = async () => {
    if (!dashboardId || !supersetUrl) {
      setError('Please provide both Dashboard ID and Superset URL');
      return;
    }

    setIsLoading(true);
    setError(null);
    setIsEmbedded(false);

    try {
      // Clear previous dashboard
      if (dashboardRef.current) {
        dashboardRef.current.innerHTML = '';
      }

      await embedDashboard({
        id: dashboardId,
        supersetDomain: supersetUrl,
        mountPoint: dashboardRef.current,
        fetchGuestToken,
        dashboardUiConfig: {
          hideTitle: false,
          hideChartControls: false,
          hideTab: false,
          showCrossFilters: true,
          showRefreshButton: true,
          showDownloadButton: true,
          showFilters: true,
        },
        height: '100%',
        width: '100%',
      });

      setIsEmbedded(true);
    } catch (err) {
      console.error('Failed to embed dashboard:', err);
      setError(`Failed to embed dashboard: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const resetDashboard = () => {
    if (dashboardRef.current) {
      dashboardRef.current.innerHTML = '';
    }
    setIsEmbedded(false);
    setError(null);
  };

  return (
    <div className="container">
      <div className="header">
        <h1>Superset Dashboard Embedding - React Example</h1>
        <p>This example demonstrates how to embed Superset dashboards in a React application using guest tokens.</p>
      </div>

      <div className="dashboard-container">
        <div className="dashboard-header">
          <div>
            <h2>Dashboard Configuration</h2>
            <div style={{ display: 'flex', gap: '20px', alignItems: 'end' }}>
              <div className="form-group">
                <label htmlFor="supersetUrl">Superset URL:</label>
                <input
                  id="supersetUrl"
                  type="url"
                  value={supersetUrl}
                  onChange={(e) => setSupersetUrl(e.target.value)}
                  placeholder="https://your-superset-instance.com"
                />
              </div>
              <div className="form-group">
                <label htmlFor="dashboardId">Dashboard ID:</label>
                <input
                  id="dashboardId"
                  type="text"
                  value={dashboardId}
                  onChange={(e) => setDashboardId(e.target.value)}
                  placeholder="dashboard-uuid-or-id"
                />
              </div>
              <div>
                <button 
                  className="btn" 
                  onClick={embedDashboardComponent}
                  disabled={isLoading}
                >
                  {isLoading ? 'Loading...' : 'Embed Dashboard'}
                </button>
                {isEmbedded && (
                  <button 
                    className="btn" 
                    onClick={resetDashboard}
                    style={{ marginLeft: '10px', background: '#d32f2f' }}
                  >
                    Reset
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="dashboard-content">
          {error && (
            <div className="error">
              <div>
                <h3>Error</h3>
                <p>{error}</p>
                <button className="btn" onClick={resetDashboard}>
                  Try Again
                </button>
              </div>
            </div>
          )}
          
          {isLoading && (
            <div className="loading">
              <div>
                <h3>Loading Dashboard...</h3>
                <p>Please wait while we fetch the guest token and embed the dashboard.</p>
              </div>
            </div>
          )}

          {!isLoading && !error && !isEmbedded && (
            <div className="loading">
              <div>
                <h3>Ready to Embed</h3>
                <p>Configure your dashboard settings above and click "Embed Dashboard" to get started.</p>
              </div>
            </div>
          )}

          <div 
            ref={dashboardRef}
            style={{ 
              height: '100%', 
              width: '100%',
              display: isEmbedded ? 'block' : 'none'
            }}
          />
        </div>
      </div>

      <div className="header" style={{ marginTop: '20px' }}>
        <h3>Instructions</h3>
        <ol>
          <li>Make sure your Superset backend API is running on <code>http://localhost:8001</code></li>
          <li>Update the Superset URL to match your instance</li>
          <li>Enter the Dashboard ID (UUID, numeric ID, or full URL)</li>
          <li>Click "Embed Dashboard" to load the dashboard</li>
        </ol>
        
        <h4>Features Demonstrated:</h4>
        <ul>
          <li>✅ Guest token generation and management</li>
          <li>✅ Dynamic dashboard embedding</li>
          <li>✅ Error handling and loading states</li>
          <li>✅ Responsive design</li>
          <li>✅ Row Level Security (RLS) support</li>
        </ul>
      </div>
    </div>
  );
}

export default App;
