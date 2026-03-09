# EducationLM

Local adaptive tutoring chat app powered by Ollama (`granite4:7b-a1b-h`) with:
- learner profile tracking (`profile.md`)
- quiz-driven mastery updates
- model tool-calling (YouTube recommender)
- context compaction for long chats

## Project Structure
- `profile.md`: active student memory profile (persistent).
- `web/`: local web chat UI + backend server.
- `tools/`: local tool implementations (for example, YouTube recommender).
- `docs/`: workflow and templates.

## Quick Start
1. Ensure Ollama is running locally.
2. Ensure model exists:
```bash
ollama pull granite4:7b-a1b-h
```
3. Start the app:
```bash
python3 web/server.py
```
4. Open:
- `http://127.0.0.1:8787`

## Tests
Run recommender tests:
```bash
python3 -m unittest -v tests/test_youtube_recommender.py
```

## Core Features
- Adaptive tutoring via system prompt + student profile context.
- Markdown + LaTeX rendering in assistant responses.
- Tool-calling for `recommend_youtube_videos` when deeper understanding resources are needed.
- Profile-aware personalization using `profile.md`.

## Memory Model
1. Session memory:
- Current conversation turns from the browser (`messages[]`).

2. Persistent learner memory:
- `profile.md` stores goals, mastery map, learner type signals, and quiz logs.

3. Tool memory:
- Tool outputs are used in-turn; persist important outcomes to `profile.md`.

## Context Compaction
When context grows too large, backend compaction is applied automatically:
- keeps recent turns verbatim
- summarizes older turns into a system memory summary
- compacts profile context to priority sections

Compaction metadata is returned in `/api/chat` response:
- `meta.profile_compacted`
- `meta.conversation_compacted`
- `meta.context_chars`
- `meta.max_context_chars`

## Environment Variables
- `OLLAMA_URL` (default `http://127.0.0.1:11434`)
- `OLLAMA_MODEL` (default `granite4:7b-a1b-h`)
- `CHAT_HOST` (default `127.0.0.1`)
- `CHAT_PORT` (default `8787`)
- `CHAT_TOOLS_ENABLED` (default `true`)
- `CHAT_MAX_CONTEXT_CHARS` (default `24000`)
- `CHAT_PROFILE_MAX_CHARS` (default `6000`)
- `CHAT_RECENT_MESSAGE_COUNT` (default `12`)
- `CHAT_SUMMARY_LINE_LIMIT` (default `24`)

## Documentation
- `docs/README.md`: profile usage and CI/CD-style learning loop.
- `docs/tutoring-protocol.md`: per-session tutoring protocol.
- `docs/session-summary.template.md`: session summary template.
- `docs/mcp-tools.md`: tool-calling design and YouTube recommender behavior.
- `web/README.md`: web app runtime details.
