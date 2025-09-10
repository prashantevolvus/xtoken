# React Superset Embedding Example

This React application demonstrates how to embed Superset dashboards using the guest token API.

## Features

- ✅ Dynamic dashboard embedding
- ✅ Guest token management
- ✅ Error handling and loading states
- ✅ Responsive design
- ✅ Row Level Security (RLS) support
- ✅ Interactive configuration

## Prerequisites

1. **Backend API**: Make sure the Superset Guest Token Generator API is running on `http://localhost:8001`
2. **Node.js**: Version 14 or higher
3. **Superset Instance**: Access to a Superset instance with guest token functionality

## Installation

1. **Install dependencies**:
   ```bash
   cd examples/react-app
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm start
   ```

3. **Open your browser**: Navigate to `http://localhost:3000`

## Usage

1. **Configure Dashboard**:
   - Enter your Superset URL (e.g., `https://your-superset-instance.com`)
   - Enter the Dashboard ID (UUID, numeric ID, or full URL)

2. **Embed Dashboard**:
   - Click "Embed Dashboard" to load the dashboard
   - The app will automatically fetch a guest token from the backend

3. **Features**:
   - Full dashboard functionality (filters, downloads, refresh)
   - Responsive design that works on mobile and desktop
   - Error handling with retry options

## Configuration

### Environment Variables

You can create a `.env` file in the `examples/react-app` directory:

```env
REACT_APP_SUPERSET_URL=https://your-superset-instance.com
REACT_APP_DEFAULT_DASHBOARD_ID=your-default-dashboard-id
REACT_APP_API_BASE_URL=http://localhost:8001
```

### Customization

The app can be customized by modifying:

- **Dashboard Configuration**: Update `dashboardUiConfig` in `App.js`
- **Styling**: Modify `src/App.css` and `src/index.css`
- **API Endpoints**: Change the fetch URL in the `fetchGuestToken` function

## API Integration

The React app communicates with the backend API:

```javascript
// Fetch guest token
const response = await fetch('/generate-token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    dashboard: dashboardId,
    rls: [] // Add RLS rules here
  }),
});
```

## Production Deployment

1. **Build the app**:
   ```bash
   npm run build
   ```

2. **Deploy**: The `build` folder contains the production-ready files

3. **Configure**: Update API endpoints and Superset URLs for production

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the backend API is running and accessible
2. **Token Generation Fails**: Check Superset credentials and URL
3. **Dashboard Not Loading**: Verify dashboard ID and Superset instance accessibility

### Debug Mode

Enable React Developer Tools and check the browser console for detailed error messages.

## License

MIT License - see the main project LICENSE file for details.
