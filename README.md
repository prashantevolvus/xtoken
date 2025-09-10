# Superset Guest Token Generator & Embedding Solution

A comprehensive solution for generating Superset guest tokens and embedding dashboards securely in web applications. This project provides a FastAPI backend for token generation and a complete embedding setup with proper security configurations.

## 🚀 Features

- **Guest Token Generation**: Secure API for generating Superset guest tokens
- **Dashboard Embedding**: Complete HTML/JavaScript solution for embedding dashboards
- **Security Configuration**: Proper CORS, CSP, and authentication setup
- **Row Level Security (RLS)**: Support for data filtering and access control
- **Multiple Dashboard Support**: Handle UUIDs, numeric IDs, and full URLs
- **Development Server**: Built-in HTTP server for local testing

## 📋 Prerequisites

- Python 3.8+
- Superset instance with guest token functionality enabled
- Access to Superset admin credentials

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd xtoken
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   # Superset Configuration
   SUPERSET_URL=https://your-superset-instance.com
   SUPERSET_USERNAME=your_admin_username
   SUPERSET_PASSWORD=your_admin_password
   SUPERSET_LOGIN_PROVIDER=db
   
   # SSL Verification (set to false for self-signed certificates)
   VERIFY_SSL=true
   
   # Row Level Security (optional)
   RLS_JSON=[]
   ```

## 🏃‍♂️ Quick Start

### 1. Start the Token Generator API

```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8001

# Or run directly
python main.py
```

The API will be available at `http://localhost:8001`

### 2. Test the API

Visit `http://localhost:8001/docs` for interactive API documentation.

### 3. Try the Examples

Choose from two example implementations:

#### Option A: Vanilla JavaScript Example
```bash
# Start the local HTTP server
python serve_embed.py
```
Open `http://localhost:3000/embed.html` in your browser.

#### Option B: React Application Example
```bash
# Navigate to React example
cd examples/react-app

# Install dependencies
npm install

# Start the React development server
npm start
```
Open `http://localhost:3000` in your browser.

## 📚 API Documentation

### Endpoints

#### `POST /generate-token`
Generate a guest token for embedding a dashboard.

**Request Body:**
```json
{
  "dashboard": "dashboard-uuid-or-id-or-url",
  "username": "guest_via_api",
  "rls": [
    {
      "clause": "tenant_id='acme'"
    }
  ]
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "dashboard_uuid": "b713fcc3-167a-4961-ac21-2fa7e851b514",
  "message": "Guest token generated successfully"
}
```

#### `GET /dashboard/{dashboard_id}`
Get dashboard information and resolve UUID.

#### `GET /health`
Health check endpoint.

#### `GET /`
API information and available endpoints.

### Dashboard Identifier Formats

The API accepts multiple dashboard identifier formats:

- **UUID**: `b713fcc3-167a-4961-ac21-2fa7e851b514`
- **Numeric ID**: `42`
- **Full URL**: `https://superset.com/superset/dashboard/42/`

## 🔧 Superset Configuration

Add the following configuration to your Superset `config.py`:

```python

# Guest Token Configuration for Embedded Dashboards
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"
GUEST_TOKEN_JWT_EXP_SECONDS = 600
GUEST_ROLE_NAME = "EmbedGuest"

# Talisman Security Configuration
TALISMAN_ENABLED = True
TALISMAN_CONFIG = {
    # IMPORTANT: List every host that's allowed to embed your Superset
    "content_security_policy": {
        "default-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "script-src": ["'self'"],
        "style-src": ["'self'", "'unsafe-inline'"],
        # Your web app domains that will host the iframe go here:
        "frame-ancestors": [
            "https://demo.app.io",
            "https://sandbox-app.app.io", 
            "https://sandbox-app.example.io",
            "http://localhost:3000"
        ],
    },
    # Tell browsers not to block iframes from other origins
    "frame_options": None,
}

# CORS & Cookies Configuration (often needed in cross-site embeds)
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "origins": [
        "https://demo.app.io",
        "https://sandbox-app.app.io", 
        "https://sandbox-app.example.io",
        "http://localhost:3000"
    ],
}

# If your embed is cross-site and you use cookies/sessions, keep these aligned:
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True  # True if you're serving over HTTPS (recommended)

#################################################
```

## 🎯 Usage Examples

### Example Implementations

This project includes two complete example implementations:

#### 1. Vanilla JavaScript Example (`examples/vanilla-js/`)
- **File**: `embed.html`
- **Features**: Simple HTML/CSS/JavaScript implementation
- **Best for**: Quick prototyping, simple integrations
- **Setup**: Just serve the HTML file with a web server

#### 2. React Application Example (`examples/react-app/`)
- **Features**: Full React application with state management
- **Best for**: Production applications, complex UIs
- **Setup**: Standard React development workflow

### JavaScript Integration

```javascript
// Fetch guest token from your backend
async function fetchGuestToken() {
  const response = await fetch("http://localhost:8001/generate-token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      dashboard: "your-dashboard-uuid",
      rls: [{ clause: "tenant_id='acme'" }]
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch token from backend");
  }

  const data = await response.json();
  return data.token;
}

// Embed the dashboard
await supersetEmbeddedSdk.embedDashboard({
  id: "your-dashboard-uuid",
  supersetDomain: "https://your-superset-instance.com",
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

### Python Client Example

```python
import requests

# Generate guest token
response = requests.post("http://localhost:8001/generate-token", json={
    "dashboard": "your-dashboard-uuid",
    "rls": [{"clause": "tenant_id='acme'"}]
})

token_data = response.json()
guest_token = token_data["token"]
```

## 🔒 Security Considerations

### Row Level Security (RLS)

Implement data filtering using RLS rules:

```json
{
  "rls": [
    {
      "clause": "tenant_id='acme'"
    },
    {
      "clause": "user_role='viewer'"
    }
  ]
}
```

### CORS Configuration

Ensure your Superset instance allows requests from your application domains:

```python
CORS_OPTIONS = {
    "supports_credentials": True,
    "origins": [
        "https://your-app-domain.com",
        "http://localhost:3000"  # For development
    ],
}
```

### Content Security Policy

Configure CSP to allow iframe embedding:

```python
"frame-ancestors": [
    "https://your-app-domain.com",
    "http://localhost:3000"
]
```

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure your Superset CORS configuration includes your domain
   - Check that `ENABLE_CORS = True` in Superset config

2. **Token Generation Fails**
   - Verify Superset credentials in `.env`
   - Check Superset URL is accessible
   - Ensure guest token functionality is enabled in Superset

3. **Dashboard Not Loading**
   - Verify dashboard UUID/ID is correct
   - Check browser console for errors
   - Ensure Superset instance is accessible from your domain

4. **SSL Certificate Issues**
   - Set `VERIFY_SSL=false` in `.env` for self-signed certificates
   - Ensure proper SSL configuration in production

### Debug Mode

Enable debug logging by setting environment variables:

```env
LOG_LEVEL=DEBUG
```

## 📁 Project Structure

```
xtoken/
├── main.py                    # FastAPI application for token generation
├── serve_embed.py             # Local HTTP server for embedding demo
├── superset_confif.txt        # Superset configuration template
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
├── README.md                 # This file
└── examples/                 # Example implementations
    ├── vanilla-js/           # Plain HTML/CSS/JavaScript example
    │   ├── embed.html        # Complete embedding example
    │   └── README.md         # Vanilla JS setup guide
    └── react-app/            # React application example
        ├── package.json      # React dependencies
        ├── public/           # React public files
        ├── src/              # React source code
        │   ├── App.js        # Main React component
        │   ├── App.css       # Component styles
        │   ├── index.js      # React entry point
        │   └── index.css     # Global styles
        └── README.md         # React setup guide
```

## 📖 Example Implementations

### Vanilla JavaScript Example

Located in `examples/vanilla-js/`, this is a simple HTML/CSS/JavaScript implementation perfect for:

- **Quick prototyping**
- **Simple integrations**
- **Learning the basics**
- **No build process required**

**Features:**
- Single HTML file with embedded CSS and JavaScript
- Fullscreen support
- Responsive design
- Error handling
- Guest token management

**Quick Start:**
```bash
# Start backend API
uvicorn main:app --reload --port 8001

# Start web server
python serve_embed.py

# Open http://localhost:3000/embed.html
```

### React Application Example

Located in `examples/react-app/`, this is a full React application ideal for:

- **Production applications**
- **Complex user interfaces**
- **State management**
- **Component-based architecture**

**Features:**
- Modern React with hooks
- Dynamic dashboard configuration
- Loading states and error handling
- Responsive design
- Interactive UI for testing different dashboards

**Quick Start:**
```bash
# Start backend API
uvicorn main:app --reload --port 8001

# Start React app
cd examples/react-app
npm install
npm start

# Open http://localhost:3000
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**
   - Use secure credential management
   - Set `VERIFY_SSL=true` for production
   - Configure proper CORS origins

2. **Security**
   - Use HTTPS in production
   - Implement proper authentication for your API
   - Configure firewall rules

3. **Performance**
   - Use a production ASGI server (Gunicorn with Uvicorn workers)
   - Implement caching for frequently accessed tokens
   - Monitor API performance

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review Superset documentation
3. Create an issue in the repository

## 🔄 Version History

- **v1.0.0**: Initial release with basic token generation and embedding
- **v1.1.0**: Added RLS support and improved error handling
- **v1.2.0**: Enhanced security configuration and documentation

---

**Note**: This solution is designed for secure embedding of Superset dashboards. Always follow security best practices and test thoroughly in your environment.