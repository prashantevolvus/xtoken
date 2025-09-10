# Vanilla JavaScript Superset Embedding Example

This example demonstrates how to embed Superset dashboards using plain HTML, CSS, and JavaScript without any frameworks.

## Features

- ✅ Simple HTML/CSS/JavaScript implementation
- ✅ Guest token management
- ✅ Fullscreen support
- ✅ Responsive design
- ✅ Error handling
- ✅ No build process required

## Prerequisites

1. **Backend API**: Make sure the Superset Guest Token Generator API is running on `http://localhost:8001`
2. **Web Server**: Use the provided `serve_embed.py` or any web server to serve the HTML file
3. **Superset Instance**: Access to a Superset instance with guest token functionality

## Quick Start

1. **Start the backend API**:
   ```bash
   # From the project root
   uvicorn main:app --reload --port 8001
   ```

2. **Start the web server**:
   ```bash
   # From the project root
   python serve_embed.py
   ```

3. **Open your browser**: Navigate to `http://localhost:3000/embed.html`

## Manual Setup

If you prefer to serve the file manually:

1. **Start the backend API** (as above)

2. **Serve the HTML file** using any web server:
   ```bash
   # Using Python's built-in server
   cd examples/vanilla-js
   python -m http.server 3000
   
   # Or using Node.js http-server
   npx http-server -p 3000
   
   # Or any other web server
   ```

3. **Open**: Navigate to `http://localhost:3000/embed.html`

## Configuration

### Dashboard Settings

Edit the JavaScript variables in `embed.html`:

```javascript
const SUPERSET_HOST = "https://your-superset-instance.com";
const DASHBOARD_ID = "your-dashboard-uuid-or-id";
```

### API Endpoint

Update the API endpoint if your backend runs on a different port:

```javascript
const response = await fetch("http://localhost:8001/generate-token", {
  // ... rest of the configuration
});
```

## Features Explained

### Guest Token Fetching

```javascript
async function fetchGuestToken() {
  const response = await fetch("http://localhost:8001/generate-token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dashboard: DASHBOARD_ID }),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch token from backend");
  }

  const data = await response.json();
  return data.token;
}
```

### Dashboard Embedding

```javascript
await supersetEmbeddedSdk.embedDashboard({
  id: DASHBOARD_ID,
  supersetDomain: SUPERSET_HOST,
  mountPoint: document.getElementById("dashboard"),
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
  height: "100%",
  width: "100%",
});
```

### Fullscreen Support

The example includes a fullscreen toggle button:

```javascript
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
  } else {
    document.exitFullscreen();
  }
}
```

## Customization

### Styling

Modify the CSS in the `<style>` section to customize the appearance:

```css
.dashboard-container {
  width: 100%;
  height: 100%;
  padding: 0;
  box-sizing: border-box;
  background: #f5f5f5;
  position: relative;
}
```

### Dashboard Configuration

Update the `dashboardUiConfig` object to customize dashboard features:

```javascript
dashboardUiConfig: {
  hideTitle: false,           // Show/hide dashboard title
  hideChartControls: false,   // Show/hide chart controls
  hideTab: false,            // Show/hide tabs
  showCrossFilters: true,    // Enable cross-filtering
  showRefreshButton: true,   // Show refresh button
  showDownloadButton: true,  // Show download options
  showFilters: true,         // Show filter panel
}
```

## Row Level Security (RLS)

To add RLS rules, modify the fetch request:

```javascript
body: JSON.stringify({ 
  dashboard: DASHBOARD_ID,
  rls: [
    { clause: "tenant_id='acme'" },
    { clause: "user_role='viewer'" }
  ]
}),
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: 
   - Ensure the backend API is running on the correct port
   - Check that the API allows requests from your domain

2. **Token Generation Fails**:
   - Verify Superset credentials in the backend `.env` file
   - Check that the Superset URL is accessible

3. **Dashboard Not Loading**:
   - Verify the dashboard ID is correct
   - Check browser console for error messages
   - Ensure the Superset instance is accessible

4. **File Not Loading**:
   - Make sure you're serving the file through a web server (not opening directly)
   - Check that the file path is correct

### Debug Mode

Open browser developer tools (F12) and check the console for detailed error messages.

## Browser Compatibility

This example works in all modern browsers that support:
- ES6+ JavaScript features
- Fetch API
- Fullscreen API
- CSS Grid and Flexbox

## Production Deployment

1. **Update URLs**: Change localhost URLs to production endpoints
2. **HTTPS**: Ensure all connections use HTTPS in production
3. **Error Handling**: Add more robust error handling for production use
4. **Security**: Implement proper authentication and authorization

## License

MIT License - see the main project LICENSE file for details.
