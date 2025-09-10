const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// Serve static files
app.use(express.static('.'));

// Serve the HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'chatbot-web' });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Chatbot web interface running on http://0.0.0.0:${PORT}`);
});
