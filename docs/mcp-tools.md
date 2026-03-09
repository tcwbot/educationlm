# MCP-Style Model Tools

This project now supports model tool-calling in the chat backend for local Ollama usage.

## Implemented Tool
- `recommend_youtube_videos`
  - implementation: `tools/youtube_recommender.py`

### Purpose
When a student needs further understanding, the model can call this tool to fetch relevant YouTube learning resources.

### Input Arguments
- `topic` (required)
- `learning_goal` (optional)
- `learner_level` (`beginner` | `intermediate` | `advanced`)
- `max_results` (1-8)

### Output
Structured JSON containing:
- `recommendations`: list of `{ title, url }`
- `fallback_search_url`: YouTube search link
- context fields (`topic`, `learning_goal`, `learner_level`)

## Runtime Flow
1. Frontend sends chat message to `/api/chat`.
2. Backend calls Ollama with tool schemas.
3. If model returns `tool_calls`, backend executes matching local tool.
4. Backend sends tool output back to the model.
5. Final assistant response is returned to UI.

## Notes
- Tool search uses DuckDuckGo HTML results filtered to YouTube links.
- If parsing fails, a fallback YouTube search URL is still returned.
- This is local and model-driven; no external API keys required.
