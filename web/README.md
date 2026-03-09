# Local Web Chat (Ollama)

Web chat UI for local Ollama model `granite4:7b-a1b-h`.

## Run
```bash
python3 web/server.py
```

Then open:
- `http://127.0.0.1:8787`

## Behavior
- Uses Ollama endpoint: `http://127.0.0.1:11434` by default.
- Uses model: `granite4:7b-a1b-h` by default.
- Sends full chat history each request.
- Optionally injects `profile.md` as system context (`Include profile.md context`).
- Compacts oversized context automatically:
  - keeps recent turns
  - summarizes older turns into a system memory note
  - slices profile context to high-priority sections
- Shows a top-bar badge with compaction status from the last response.
- Prefills the chat with a default adaptive tutoring system prompt aligned to the session workflow.
- Supports model tool-calling with `recommend_youtube_videos` for extra learning resources.
- Tool use can be toggled in UI (`Enable model tools`).
- Deterministic fallback: clear YouTube/video requests force `recommend_youtube_videos` even if model tool-calling is missed.
- Includes D3 visual tracking:
  - Mastery chart (`where you are`)
  - Quiz trend + projection (`where you've been / where you're going`)
- Uses separate views for `Chat`, `Trajectory`, and `Prompt` (system prompt editor).
- Supports browser speech-to-text in Chat view (`Start Mic`) using Web Speech API.
- Supports browser text-to-speech for assistant answers:
    - per-message `Speak` button
    - `Auto-read answers` defaults to ON for new users
    - `Turn Auto-read Off/On` toggle in Chat view
    - `Stop Audio` immediately stops speech and disables auto-read
    - voice selector + rate/pitch controls (saved locally in browser)

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

## Notes
- Make sure Ollama is running before sending messages.
- Keep `profile.md` updated so charts reflect current mastery and quiz history.
- Microphone requires browser permission and Web Speech API support (best on Chrome/Edge).
- Text-to-speech uses browser Speech Synthesis API and voice availability varies by OS/browser.
- If the model is not pulled yet:
```bash
ollama pull granite4:7b-a1b-h
```
