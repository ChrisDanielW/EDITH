# EDITH Web UI

A beautiful, modern web interface for EDITH (Even Disconnected, I'm The Helper).

## Features

- 🎨 **Modern Dark Theme** - Easy on the eyes
- 💬 **Smart Chat Interface** - Natural conversations with EDITH
- 🔍 **RAG Mode Indicators** - See when EDITH is searching your notes
- 📊 **Summary Generation** - Get quick overviews of your notes
- 📈 **Database Stats** - Monitor your vector database
- ⚡ **Real-time Responses** - Fast and responsive
- 📱 **Responsive Design** - Works on desktop and mobile

## Quick Start

### 1. Install Dependencies

```powershell
pip install flask flask-cors
```

### 2. Start the Server

```powershell
# Option 1: Using the start script
python start_ui.py

# Option 2: Direct launch
python src/api/app.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

## API Endpoints

### `GET /api/health`
Health check endpoint

### `POST /api/query`
Send a query to EDITH
```json
{
  "query": "What is polymorphism?",
  "use_rag": true  // optional
}
```

### `POST /api/summary`
Generate a summary
```json
{
  "style": "comprehensive"  // or "bullet", "brief"
}
```

### `GET /api/stats`
Get vector database statistics

### `POST /api/ingest`
Ingest new documents
```json
{
  "directory": "path/to/notes"  // optional
}
```

## Keyboard Shortcuts

- `Ctrl+K` / `Cmd+K` - Focus input
- `Ctrl+L` / `Cmd+L` - Clear chat
- `Enter` - Send message
- `Shift+Enter` - New line

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (HTML/CSS/JS) │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│   Flask API     │
│   (Python)      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│     EDITH       │
│  (RAG + LLM)    │
└─────────────────┘
```

## Customization

### Colors
Edit `ui/styles.css` and modify the CSS variables in `:root`:
```css
--bg-primary: #0f0f1e;
--accent-primary: #6366f1;
/* etc. */
```

### API URL
Edit `ui/app.js` and change:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

## Troubleshooting

### "Cannot connect to EDITH API"
- Make sure the Flask server is running
- Check if port 5000 is available
- Verify firewall settings

### Slow responses
- Check if Ollama is running
- Verify GPU is being used
- Reduce `MAX_TOKENS` in `.env`

### CORS errors
- Ensure `flask-cors` is installed
- Check browser console for details

## Development

To modify the UI:

1. Edit files in `ui/` directory
2. Refresh browser (no build step needed!)
3. Check browser console for errors

## Production Deployment

For production use:

1. Use a production WSGI server (gunicorn, waitress)
2. Set up HTTPS
3. Configure CORS properly
4. Add authentication if needed

Example with gunicorn:
```powershell
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.api.app:app
```

## License

Same as EDITH - MIT License
