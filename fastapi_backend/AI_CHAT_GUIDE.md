# AI-Powered Chat & Vector Search - Complete Guide

## Overview
The AutoPM system now includes advanced AI capabilities powered by Google Gemini with vector embeddings for semantic search and intelligent chat assistance.

## Key Features

### 1. **Vector Embeddings**
- Every PR, issue, task, and comment is automatically embedded using Google's `text-embedding-004` model
- Stored in ChromaDB for fast semantic search
- Automatic embedding during sync operations
- 768-dimensional vectors for precise semantic matching

### 2. **AI Chat with RAG**
- Chat with Gemini 2.5 Flash
- Retrieval Augmented Generation (RAG) for accurate, context-aware responses
- Access to all project data (PRs, issues, tasks, comments)
- Conversation history tracking
- Project-specific filtering

### 3. **Semantic Search**
- Natural language search across all content
- Finds relevant items based on meaning, not just keywords
- Ranked by similarity score
- Filter by content type and project

## Setup Instructions

### 1. Install Dependencies
```bash
cd fastapi_backend
pip install -r requirements.txt
```

New packages added:
- `google-genai`: Google Gemini AI SDK
- `chromadb`: Vector database
- `numpy`: Numerical operations

### 2. Get Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run Database Migration
```bash
python scripts/migrate_sync_tables.py
```

This creates:
- `github_comments` - GitHub comments storage
- `jira_comments` - Jira comments storage
- `sync_logs` - Sync operation tracking
- `vector_embeddings` - Embedding metadata
- `chat_history` - Chat conversation history

### 4. Initial Embedding Generation
After running your first sync, generate embeddings for all data:

```bash
# Via API
curl -X POST "http://localhost:8000/api/ai/embeddings/generate-all" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": false}'
```

Or trigger sync which will auto-embed:
```bash
curl -X POST "http://localhost:8000/api/sync/trigger" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Endpoints

### Chat Endpoints

#### `POST /api/ai/chat`
Chat with AI assistant using RAG

**Request:**
```json
{
  "message": "What are the current open PRs that need review?",
  "project_ids": ["PRJ001"],  // Optional
  "content_types": ["pr", "issue"],  // Optional
  "conversation_history": [  // Optional
    {
      "user": "Previous question",
      "assistant": "Previous response"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "chat_id": "CHAT-EMP001-1730476800",
  "response": "Based on the current data, here are the open PRs...",
  "context_items": [
    {
      "id": "repo/PR#123",
      "content_type": "pr",
      "document": "Title: Fix authentication...",
      "metadata": {...},
      "similarity_score": 0.85
    }
  ],
  "context_count": 10,
  "timestamp": "2025-11-01T10:30:00Z"
}
```

#### `GET /api/ai/chat/history?limit=20`
Get conversation history

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "chat_id": "CHAT-EMP001-1730476800",
      "message": "What are the open PRs?",
      "response": "Here are the open PRs...",
      "context_items": ["repo/PR#123", "repo/PR#456"],
      "timestamp": "2025-11-01T10:30:00Z"
    }
  ],
  "count": 20
}
```

#### `GET /api/ai/chat/suggestions?project_id=PRJ001`
Get suggested questions

**Response:**
```json
{
  "success": true,
  "suggestions": [
    "What are the current open PRs that need review?",
    "Show me high priority issues that are unassigned",
    "What are the blocked tasks and their dependencies?",
    ...
  ]
}
```

### Search Endpoints

#### `POST /api/ai/search`
Semantic search across all data

**Request:**
```json
{
  "query": "authentication bugs with high priority",
  "content_types": ["issue", "pr"],  // Optional
  "project_ids": ["PRJ001"],  // Optional
  "n_results": 10
}
```

**Response:**
```json
{
  "success": true,
  "query": "authentication bugs with high priority",
  "results": [
    {
      "id": "repo/Issue#789",
      "content_type": "issue",
      "document": "Title: Auth token refresh failing...",
      "metadata": {
        "issue_id": "repo/Issue#789",
        "priority": "High",
        "status": "Open"
      },
      "similarity_score": 0.92
    }
  ],
  "count": 10,
  "timestamp": "2025-11-01T10:30:00Z"
}
```

### Embedding Management

#### `POST /api/ai/embeddings/generate-all`
Generate embeddings for all existing data

**Request:**
```json
{
  "force_reindex": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "All embeddings generated successfully",
  "stats": {
    "prs": 450,
    "issues": 230,
    "jira_tasks": 670,
    "github_comments": 1780,
    "jira_comments": 2340,
    "errors": 0
  },
  "timestamp": "2025-11-01T10:30:00Z"
}
```

#### `GET /api/ai/embeddings/stats`
Get embedding statistics

**Response:**
```json
{
  "success": true,
  "total_embeddings": 5470,
  "by_type": {
    "pr": 450,
    "issue": 230,
    "jira_task": 670,
    "comment": 4120
  },
  "timestamp": "2025-11-01T10:30:00Z"
}
```

### Analysis Endpoints

#### `POST /api/ai/analyze/project-summary`
AI-powered project status summary

**Request:**
```json
{
  "project_id": "PRJ001"
}
```

**Response:**
```json
{
  "success": true,
  "project_id": "PRJ001",
  "summary": "## Project Health: Yellow\n\n### Achievements\n- 15 PRs merged this week...",
  "context_items_analyzed": 20,
  "timestamp": "2025-11-01T10:30:00Z"
}
```

#### `POST /api/ai/analyze/sentiment?text=This%20is%20blocking%20the%20release`
Analyze sentiment of text

**Response:**
```json
{
  "success": true,
  "text": "This is blocking the release",
  "analysis": {
    "sentiment": "Urgent",
    "is_blocker": true,
    "is_critical": true,
    "summary": "Text indicates a critical blocker affecting release"
  },
  "timestamp": "2025-11-01T10:30:00Z"
}
```

### System Status

#### `GET /api/ai/status`
Check AI system health

**Response:**
```json
{
  "success": true,
  "services": {
    "embedding": "operational",
    "vector_db": "operational",
    "chat": "operational"
  },
  "embedding_dimensions": 768,
  "timestamp": "2025-11-01T10:30:00Z"
}
```

## Example Use Cases

### 1. Find Open PRs Needing Review
```bash
curl -X POST "http://localhost:8000/api/ai/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the open PRs that need review?",
    "content_types": ["pr"]
  }'
```

### 2. Find High Priority Bugs
```bash
curl -X POST "http://localhost:8000/api/ai/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "critical bugs high priority",
    "content_types": ["issue", "jira_task"],
    "n_results": 5
  }'
```

### 3. Analyze Project Status
```bash
curl -X POST "http://localhost:8000/api/ai/analyze/project-summary" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PRJ001"
  }'
```

### 4. Search Across Comments
```bash
curl -X POST "http://localhost:8000/api/ai/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "performance optimization discussion",
    "content_types": ["comment"],
    "n_results": 10
  }'
```

## Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────────────────────────────────────┐
│         FastAPI Backend                         │
│                                                  │
│  ┌──────────────┐      ┌──────────────┐        │
│  │ Chat Routes  │──────▶│Chat Service  │        │
│  └──────────────┘      └──────┬───────┘        │
│                                │                 │
│  ┌──────────────┐      ┌──────▼───────┐        │
│  │ Sync Routes  │──────▶│Vector Service│        │
│  └──────────────┘      └──────┬───────┘        │
│                                │                 │
└────────────────────────────────┼─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐       ┌────────▼────────┐
            │ Google Gemini  │       │   ChromaDB      │
            │  - Embeddings  │       │  - Vector Store │
            │  - Chat (2.5)  │       │  - Similarity   │
            └────────────────┘       └─────────────────┘
```

## Data Flow

### Sync → Embed Flow
```
1. Sync Service fetches PR/Issue/Task from GitHub/Jira
2. Saves to PostgreSQL/MySQL database
3. Vector Service generates embedding using Gemini
4. Stores embedding in ChromaDB + metadata in DB
5. Ready for semantic search
```

### Chat Flow
```
1. User sends question
2. Vector Service generates query embedding
3. ChromaDB searches for similar vectors
4. Top N relevant items retrieved
5. Context + Question sent to Gemini 2.5 Flash
6. AI generates response using RAG
7. Response + context returned to user
8. Conversation saved to history
```

## Performance Considerations

### Embedding Generation
- **Speed**: ~100-200 items per minute
- **Initial Load**: Large datasets may take 10-30 minutes
- **Automatic**: New items embedded during sync
- **Incremental**: Only new/updated items re-embedded

### Vector Search
- **Query Speed**: <100ms for most searches
- **Accuracy**: High semantic similarity
- **Scale**: Efficient for 100K+ documents

### Chat Response Time
- **Search**: ~100ms
- **Gemini API**: ~1-3 seconds
- **Total**: ~1-3 seconds typical response time

## Storage Requirements

### ChromaDB
- **Location**: `./chroma_db/` directory
- **Size**: ~1KB per embedding
- **Growth**: Linear with content volume

### Database
- **vector_embeddings**: Text + metadata (~2KB per item)
- **chat_history**: Conversations (~1KB per exchange)

## Best Practices

### 1. Sync & Embed Regularly
- Enable periodic sync (runs every 60s)
- New data automatically embedded
- No manual intervention needed

### 2. Ask Specific Questions
Good:
- "Show me open PRs with failing builds in project X"
- "What are the critical bugs assigned to John?"
- "List blocked tasks with dependencies"

Bad:
- "Tell me about the project"
- "What's happening?"

### 3. Use Filters
- Specify `project_ids` to narrow scope
- Use `content_types` to focus search
- Improves relevance and speed

### 4. Monitor Embeddings
```bash
# Check stats regularly
curl http://localhost:8000/api/ai/embeddings/stats
```

### 5. Conversation Context
- Include recent conversation history
- Helps AI understand context
- Improves follow-up questions

## Troubleshooting

### Issue: No embeddings generated
**Solution:**
```bash
# Manually trigger embedding
curl -X POST http://localhost:8000/api/ai/embeddings/generate-all \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"force_reindex": true}'
```

### Issue: Poor search results
**Causes:**
- Insufficient data synced
- Query too vague
- Content not embedded yet

**Solution:**
- Run sync first
- Be more specific in queries
- Check embedding stats

### Issue: Slow responses
**Causes:**
- Large context retrieval
- Gemini API latency
- Network issues

**Solution:**
- Reduce `n_results` parameter
- Check network connection
- Monitor Gemini API status

### Issue: API key errors
**Solution:**
```bash
# Verify key in .env
cat .env | grep GEMINI_API_KEY

# Test key
curl -X GET http://localhost:8000/api/ai/status
```

## Cost Considerations

### Google Gemini API
- **Embeddings**: Free tier available
- **Chat**: Pay per token
- **Typical Cost**: $0.01 - $0.10 per 1000 requests

### Storage
- **ChromaDB**: Local, no cost
- **Database**: Standard SQL storage costs

## Security

### API Key Protection
- Store in `.env` file
- Never commit to git
- Use environment variables

### Access Control
- All endpoints require authentication
- JWT token validation
- User-based chat history

## Future Enhancements

Planned features:
- [ ] Webhook-based real-time embedding
- [ ] Multi-modal embeddings (images, code)
- [ ] Custom fine-tuned models
- [ ] Advanced analytics dashboards
- [ ] Team collaboration features
- [ ] Voice interface

## Support & Resources

- **Google Gemini Docs**: https://ai.google.dev/docs
- **ChromaDB Docs**: https://docs.trychroma.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## Summary

The AI-powered chat and vector search system provides:
- ✅ Automatic embedding of all synced data
- ✅ Natural language chat with project context
- ✅ Semantic search across all content
- ✅ Project status analysis
- ✅ Sentiment analysis
- ✅ Conversation history
- ✅ Real-time data access

All integrated seamlessly with the existing AutoPM system!
