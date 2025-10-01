# Nginx Frontend Container

This container provides a modern, responsive web interface for the MCP Notebook Agent system using nginx as a reverse proxy and static file server.

## Features

### 🎨 **Beautiful UI**
- Modern gradient design with glassmorphism effects
- Responsive layout that works on desktop and mobile
- Font Awesome icons for visual appeal
- Smooth animations and transitions
- Dark/light theme support

### 🚀 **Core Functionality**
- **Agent Task Interface**: Submit tasks to the AI agent with custom descriptions
- **Real-time Status**: Monitor agent and MCP server connection status
- **Progress Tracking**: Visual progress bars during task execution
- **Notebook Management**: View, download, and delete saved notebooks
- **Quick Actions**: Pre-defined task templates for common use cases

### 🛠 **Technical Features**
- **Reverse Proxy**: Routes API calls to appropriate backend services
- **Static File Serving**: Optimized delivery of HTML/CSS/JS assets
- **Gzip Compression**: Reduces bandwidth usage
- **Error Handling**: Custom error pages for service unavailability
- **Auto-refresh**: Periodic status checks and notebook list updates

## File Structure

```
nginxContainer/
├── Dockerfile              # Container build configuration
├── nginx.conf              # Nginx server configuration
└── static/                 # Static web assets
    ├── index.html          # Main dashboard page
    ├── styles.css          # Modern CSS styling
    ├── script.js           # Interactive JavaScript
    └── 50x.html           # Error page template
```

## API Integration

The frontend integrates with the following services:

### Agent API (via nginx proxy)
- `POST /api/v1/agent/run` - Execute agent tasks
- `GET /api/v1/agent/download/{filename}` - Download notebooks
- `GET /api/v1/agent/notebook/{filename}` - Get notebook info

### System Status
- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - Detailed system status

### Notebook Management
- `GET /api/v1/notebooks` - List saved notebooks
- `DELETE /api/v1/notebooks/{filename}` - Delete notebooks

## Usage Examples

### 1. Basic Task Execution
1. Enter a task description in the text area
2. Optionally specify a custom filename
3. Click "Run Agent" to execute
4. Monitor progress and download results

### 2. Quick Actions
Use pre-defined templates for common tasks:
- **ML Examples**: Machine learning with scikit-learn
- **Data Viz**: Visualization with matplotlib/seaborn
- **Web Scraping**: BeautifulSoup and requests
- **Pandas Tutorial**: Data manipulation examples
- **Statistics**: scipy and numpy examples
- **Deep Learning**: TensorFlow/Keras examples

### 3. Notebook Management
- View all saved notebooks in a grid layout
- Download notebooks directly to your computer
- Delete unwanted notebooks
- Auto-refresh to see new notebooks

## Keyboard Shortcuts

- `Ctrl+Enter`: Run the current agent task
- `Ctrl+R`: Refresh the notebooks list
- `Escape`: Clear the current task

## Responsive Design

The interface adapts to different screen sizes:
- **Desktop**: Full-featured layout with sidebar
- **Tablet**: Responsive grid layouts
- **Mobile**: Stacked layout with touch-friendly controls

## Customization

### Themes
Modify `styles.css` to change:
- Color schemes (gradients, accents)
- Fonts and typography
- Spacing and layout
- Animation effects

### Quick Actions
Add new quick action buttons by modifying the `actions-grid` section in `index.html`:

```html
<button class="action-btn" data-task="Your custom task description">
    <i class="fas fa-your-icon"></i>
    <span>Your Action</span>
</button>
```

### API Endpoints
Update the `ENDPOINTS` object in `script.js` to modify API routes:

```javascript
const ENDPOINTS = {
    customEndpoint: `${API_BASE}/custom/route`,
    // ... other endpoints
};
```

## Performance Features

- **Lazy Loading**: Images and content load as needed
- **Caching**: Static assets cached by nginx
- **Compression**: Gzip compression for faster loading
- **Minification**: CSS and JS can be minified for production

## Security

- **Proxy Configuration**: Secure routing to backend services
- **CORS Handling**: Proper cross-origin request handling
- **Input Validation**: Client-side validation for user inputs
- **Error Boundaries**: Graceful error handling

## Development

### Local Development
1. Modify files in the `static/` directory
2. Rebuild the container: `docker-compose build nginx-frontend`
3. Restart: `docker-compose restart nginx-frontend`

### Adding New Features
1. Update HTML structure in `index.html`
2. Add styling in `styles.css`
3. Implement functionality in `script.js`
4. Test with the backend APIs

## Troubleshooting

### Common Issues

**502 Bad Gateway**: Backend services not running
- Check if agent and MCP services are healthy
- Verify docker network connectivity

**Static Files Not Loading**: Build or mount issues
- Rebuild the nginx container
- Check file permissions

**API Calls Failing**: Proxy configuration
- Verify nginx.conf proxy settings
- Check backend service URLs

### Debug Mode
Enable debug logging in nginx.conf:
```nginx
error_log /var/log/nginx/error.log debug;
```

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Modern CSS features used:
- CSS Grid and Flexbox
- CSS Variables
- Backdrop filters
- CSS animations