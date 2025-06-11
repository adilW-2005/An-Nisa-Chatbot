# AnNisa.org AI Chatbot

A complete AI-powered chatbot for AnNisa.org that uses Retrieval Augmented Generation (RAG) to answer questions about the organization using content scraped from their website.

## Features

- **Web Scraping**: Automatically crawls AnNisa.org content
- **Vector Search**: Uses sentence-transformers and FAISS for semantic search
- **AI Responses**: Integrates with OpenAI GPT-4 for intelligent answers
- **React Frontend**: Modern, responsive chat interface
- **Flask Backend**: RESTful API with RAG capabilities
- **Source Attribution**: Shows sources for all answers

## Project Structure

```
annisa-chatbot/
├── backend/
│   ├── ingest.py           # Web scraping and embedding script
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   ├── env.example         # Environment variables template
│   └── data/               # Generated knowledge base files
├── frontend/
│   ├── src/
│   │   ├── Chat.jsx        # Main chat component
│   │   ├── Chat.css        # Chat styling
│   │   ├── App.js          # App component
│   │   ├── App.css         # App styling
│   │   └── index.js        # React entry point
│   ├── public/
│   │   └── index.html      # HTML template
│   └── package.json        # React dependencies
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- OpenAI API key

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd annisa-chatbot/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Create knowledge base:**
   ```bash
   python ingest.py
   ```
   This will:
   - Scrape content from AnNisa.org
   - Create text chunks
   - Generate embeddings
   - Build FAISS index
   - Save to `data/` directory

6. **Start Flask server:**
   ```bash
   python app.py
   ```
   Server will run on http://localhost:5000

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd annisa-chatbot/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start React development server:**
   ```bash
   npm start
   ```
   Frontend will run on http://localhost:3000

## Usage

1. **Start both servers** (backend and frontend)
2. **Open browser** to http://localhost:3000
3. **Ask questions** about AnNisa.org such as:
   - "What is AnNisa.org's mission?"
   - "How can I volunteer?"
   - "What programs do you offer?"
   - "How do I donate?"

## API Endpoints

### Backend API (http://localhost:5000)

- `GET /` - Health check
- `POST /chat` - Main chat endpoint
  ```json
  {
    "message": "What is AnNisa.org?"
  }
  ```
  
  Response:
  ```json
  {
    "response": "AnNisa.org is...",
    "sources": ["https://annisa.org/about"],
    "chunks_used": 3
  }
  ```

- `POST /search` - Search knowledge base (debugging)

## Technical Details

### RAG Pipeline

1. **Ingestion**: Web scraping → Text chunking → Embedding generation → FAISS indexing
2. **Retrieval**: Query embedding → Similarity search → Top-k relevant chunks
3. **Generation**: Context + Query → OpenAI GPT-4 → Contextual response

### Dependencies

**Backend:**
- Flask + CORS for API
- BeautifulSoup for web scraping
- sentence-transformers for embeddings
- FAISS for vector search
- OpenAI for response generation

**Frontend:**
- React for UI framework
- Modern CSS for styling
- Fetch API for backend communication

## Customization

### Adding New Pages to Crawl

Edit `target_pages` in `ingest.py`:

```python
self.target_pages = [
    "/",
    "/about",
    "/new-page",  # Add new pages here
    # ... existing pages
]
```

### Modifying Chunk Size

Adjust parameters in `ingest.py`:

```python
def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50):
```

### Changing AI Model

Update `app.py`:

```python
response = self.openai_client.ChatCompletion.create(
    model="gpt-3.5-turbo",  # Change model here
    # ... rest of parameters
)
```

## Troubleshooting

### Common Issues

1. **"Knowledge base not found"**
   - Run `python ingest.py` first

2. **"OPENAI_API_KEY not found"**
   - Copy `env.example` to `.env`
   - Add your OpenAI API key

3. **"Failed to send message"**
   - Ensure Flask backend is running
   - Check CORS settings

4. **Empty responses**
   - Check if website content was scraped successfully
   - Verify FAISS index was created

### Debug Mode

Enable debug logging in `app.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Performance Notes

- **Initial setup**: Ingestion may take 2-5 minutes depending on website size
- **Response time**: Typically 2-5 seconds per query
- **Memory usage**: ~500MB for embeddings model + knowledge base
- **Storage**: ~50-100MB for knowledge base files

## Deployment

### Production Deployment

1. **Backend**: Deploy Flask app to services like Heroku, AWS, or DigitalOcean
2. **Frontend**: Build and deploy to Netlify, Vercel, or AWS S3
3. **Environment**: Set production environment variables
4. **CORS**: Update CORS settings for production domains

### Environment Variables for Production

```bash
OPENAI_API_KEY=your-production-api-key
FLASK_DEBUG=False
FLASK_PORT=80
CORS_ORIGINS=https://your-frontend-domain.com
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is created for AnNisa.org. Please respect their content and terms of use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs
3. Open an issue on the repository

---

**Note**: This chatbot uses the organization's publicly available website content. Always respect robots.txt and rate limits when scraping. 