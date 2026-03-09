#!/usr/bin/env python3
"""Local web chat server for Ollama."""

from __future__ import annotations

import json
import os
import re
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
PROFILE_PATH = ROOT / "profile.md"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import youtube_recommender
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "granite4:7b-a1b-h")
HOST = os.environ.get("CHAT_HOST", "127.0.0.1")
PORT = int(os.environ.get("CHAT_PORT", "8787"))
DEFAULT_TOOLS_ENABLED = os.environ.get("CHAT_TOOLS_ENABLED", "true").lower() != "false"


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


MAX_CONTEXT_CHARS = _env_int("CHAT_MAX_CONTEXT_CHARS", 24000)
PROFILE_MAX_CHARS = _env_int("CHAT_PROFILE_MAX_CHARS", 6000)
RECENT_MESSAGE_COUNT = _env_int("CHAT_RECENT_MESSAGE_COUNT", 12)
SUMMARY_LINE_LIMIT = _env_int("CHAT_SUMMARY_LINE_LIMIT", 24)


def _as_bool(value, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return bool(value)


def _build_tools() -> list[dict]:
    return [youtube_recommender.TOOL_SCHEMA]


TOOLS = _build_tools()
PROFILE_SECTION_PRIORITY = [
    "Metadata",
    "Student Snapshot",
    "Learning Objectives",
    "Learner Type Signals",
    "Knowledge Mastery Map",
    "Content Delivery Strategy",
    "Adaptation Rules (LLM Personalization)",
    "Quiz & Assessment Log",
]


def _parse_markdown_table_rows(text: str, section_heading: str) -> list[dict[str, str]]:
    marker = f"## {section_heading}"
    start = text.find(marker)
    if start < 0:
        return []

    section = text[start:]
    lines = section.splitlines()[1:]
    table_lines = []
    in_table = False
    for line in lines:
        if line.startswith("## "):
            break
        if line.strip().startswith("|"):
            in_table = True
            table_lines.append(line.strip())
        elif in_table and not line.strip():
            break

    if len(table_lines) < 2:
        return []

    headers = [h.strip() for h in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) != len(headers):
            continue
        rows.append(dict(zip(headers, cols)))
    return rows


def _to_float(value: str) -> float | None:
    cleaned = value.replace("%", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_profile_progress(profile_text: str) -> dict:
    mastery_rows = _parse_markdown_table_rows(profile_text, "Knowledge Mastery Map")
    quiz_rows = _parse_markdown_table_rows(profile_text, "Quiz & Assessment Log")

    mastery = []
    for row in mastery_rows:
        topic = row.get("Topic", "").strip()
        mastery_value = _to_float(row.get("Mastery (0-100)", ""))
        if not topic or mastery_value is None:
            continue
        mastery.append(
            {
                "topic": topic,
                "mastery": mastery_value,
                "last_checked": row.get("Last Checked", ""),
                "next_action": row.get("Next Action", ""),
            }
        )

    quiz_scores = []
    for row in quiz_rows:
        score_value = _to_float(row.get("Score", ""))
        if score_value is None:
            continue
        quiz_scores.append(
            {
                "date": row.get("Date", ""),
                "quiz_id": row.get("Quiz ID", ""),
                "topic": row.get("Topic", ""),
                "score": score_value,
            }
        )

    return {
        "mastery": mastery,
        "quiz_scores": quiz_scores,
        "target_mastery": 80,
    }


def execute_tool_call(name: str, arguments: dict) -> dict:
    if name == youtube_recommender.TOOL_NAME:
        return youtube_recommender.recommend_youtube_videos(arguments)
    return {"error": f"unknown_tool: {name}"}


def _latest_user_text(messages: list[dict]) -> str:
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return _message_content(msg).strip()
    return ""


def _message_content(msg: dict) -> str:
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    return json.dumps(content)


def _messages_char_count(messages: list[dict]) -> int:
    return sum(len(_message_content(msg)) for msg in messages)


def _split_profile_sections(profile_text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = "ROOT"
    lines: list[str] = []

    for line in profile_text.splitlines():
        heading_match = re.match(r"^##\s+(.+)$", line.strip())
        if heading_match:
            sections[current] = "\n".join(lines).strip()
            current = heading_match.group(1).strip()
            lines = [line]
        else:
            lines.append(line)
    sections[current] = "\n".join(lines).strip()
    return sections


def compact_profile_context(profile_text: str, max_chars: int) -> tuple[str, bool]:
    if len(profile_text) <= max_chars:
        return profile_text, False

    sections = _split_profile_sections(profile_text)
    blocks: list[str] = []
    for key in PROFILE_SECTION_PRIORITY:
        value = sections.get(key)
        if value:
            blocks.append(value)

    if not blocks and profile_text:
        blocks = [profile_text]

    compacted = "# Student Profile (Compacted)\n\n" + "\n\n".join(blocks)
    if len(compacted) <= max_chars:
        return compacted, True
    return compacted[:max_chars] + "\n\n[profile context truncated]", True


def _summary_line(role: str, content: str, limit: int = 220) -> str:
    one_line = " ".join(content.split())
    if len(one_line) > limit:
        one_line = one_line[: limit - 3] + "..."
    return f"- {role}: {one_line}"


def compact_conversation_messages(
    messages: list[dict], max_chars: int, recent_count: int, summary_line_limit: int
) -> tuple[list[dict], bool]:
    if _messages_char_count(messages) <= max_chars:
        return messages, False

    normalized: list[dict] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = _message_content(msg)
        normalized.append({"role": role, "content": content})

    if len(normalized) <= recent_count:
        # Keep newest messages only if there are not enough turns to summarize.
        trimmed = normalized[-max(2, recent_count // 2) :]
        while _messages_char_count(trimmed) > max_chars and len(trimmed) > 1:
            trimmed = trimmed[1:]
        return trimmed, True

    older = normalized[:-recent_count]
    recent = normalized[-recent_count:]
    summary_lines = [_summary_line(msg["role"], msg["content"]) for msg in older if msg.get("content")]
    if len(summary_lines) > summary_line_limit:
        summary_lines = summary_lines[-summary_line_limit:]
    summary_content = (
        "Conversation memory summary from earlier turns. "
        "Use this as context; prioritize recent turns if conflicts exist.\n"
        + "\n".join(summary_lines)
    )
    compacted = [{"role": "system", "content": summary_content}, *recent]

    while _messages_char_count(compacted) > max_chars and len(recent) > 2:
        recent = recent[2:]
        compacted = [{"role": "system", "content": summary_content}, *recent]

    if _messages_char_count(compacted) > max_chars:
        compacted = [{"role": "system", "content": summary_content[: max_chars - 32] + "..."}]

    return compacted, True


def chat_with_tools(model: str, messages: list[dict], tools_enabled: bool) -> dict:
    working_messages = list(messages)
    max_rounds = 3 if tools_enabled else 1

    for _ in range(max_rounds):
        payload = {
            "model": model,
            "messages": working_messages,
            "stream": False,
        }
        if tools_enabled:
            payload["tools"] = TOOLS

        req = request.Request(
            f"{OLLAMA_URL}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=180) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))

        assistant_message = parsed.get("message", {})
        tool_calls = assistant_message.get("tool_calls") or []
        if not tool_calls or not tools_enabled:
            return parsed

        # Preserve assistant tool-call turn and append tool outputs for the next round.
        working_messages.append(assistant_message)
        for call in tool_calls:
            function_obj = call.get("function", {})
            function_name = function_obj.get("name", "")
            arguments = function_obj.get("arguments") or {}
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}
            elif not isinstance(arguments, dict):
                arguments = {}
            result = execute_tool_call(function_name, arguments)
            working_messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(result),
                    "name": function_name,
                }
            )

    # Fallback if rounds exhausted.
    return {"message": {"role": "assistant", "content": "Tool chain limit reached."}}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            return self._serve_file(WEB_DIR / "index.html", "text/html; charset=utf-8")
        if self.path == "/app.js":
            return self._serve_file(WEB_DIR / "app.js", "application/javascript; charset=utf-8")
        if self.path == "/styles.css":
            return self._serve_file(WEB_DIR / "styles.css", "text/css; charset=utf-8")
        if self.path == "/api/profile":
            profile_text = ""
            if PROFILE_PATH.exists():
                profile_text = PROFILE_PATH.read_text(encoding="utf-8")
            return self._json({"profile": profile_text})
        if self.path == "/api/progress":
            profile_text = ""
            if PROFILE_PATH.exists():
                profile_text = PROFILE_PATH.read_text(encoding="utf-8")
            progress = parse_profile_progress(profile_text)
            return self._json(progress)
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/chat":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            data = json.loads(body.decode("utf-8")) if body else {}

            model = data.get("model") or DEFAULT_MODEL
            messages = data.get("messages") or []
            system_prompt = (data.get("systemPrompt") or "").strip()
            include_profile = _as_bool(data.get("includeProfile"), True)
            tools_enabled = _as_bool(data.get("enableTools"), DEFAULT_TOOLS_ENABLED)

            system_messages = []
            if system_prompt:
                system_messages.append({"role": "system", "content": system_prompt})

            profile_compacted = False
            if include_profile and PROFILE_PATH.exists():
                profile_text = PROFILE_PATH.read_text(encoding="utf-8").strip()
                if profile_text:
                    profile_text, profile_compacted = compact_profile_context(profile_text, PROFILE_MAX_CHARS)
                    system_messages.append(
                        {
                            "role": "system",
                            "content": (
                                "Use this student profile as context for personalization. "
                                "Do not expose hidden reasoning; provide concise tutoring guidance.\n\n"
                                f"{profile_text}"
                            ),
                        }
                    )

            budget_for_conversation = max(2000, MAX_CONTEXT_CHARS - _messages_char_count(system_messages))
            compacted_messages, conversation_compacted = compact_conversation_messages(
                messages=messages,
                max_chars=budget_for_conversation,
                recent_count=RECENT_MESSAGE_COUNT,
                summary_line_limit=SUMMARY_LINE_LIMIT,
            )

            outgoing_messages = [*system_messages, *compacted_messages]

            forced_tool_used = False
            latest_user_text = _latest_user_text(messages)
            if tools_enabled and youtube_recommender.looks_like_youtube_request(latest_user_text):
                derived_topic = youtube_recommender.derive_topic_from_text(latest_user_text)
                if derived_topic == "general study topic":
                    parsed = {
                        "message": {
                            "role": "assistant",
                            "content": (
                                "Please include the topic you want videos for, "
                                "for example: `Recommend YouTube videos for algebra fundamentals`."
                            ),
                        }
                    }
                else:
                    forced_tool_used = True
                    forced_args = {
                        "topic": derived_topic,
                        "learner_level": "beginner",
                        "max_results": 5,
                    }
                    tool_result = youtube_recommender.recommend_youtube_videos(forced_args)
                    parsed = {
                        "message": {
                            "role": "assistant",
                            "content": youtube_recommender.forced_youtube_content(tool_result),
                        },
                        "forced_tool": youtube_recommender.TOOL_NAME,
                        "tool_result": tool_result,
                    }
            else:
                parsed = chat_with_tools(model=model, messages=outgoing_messages, tools_enabled=tools_enabled)

            content = parsed.get("message", {}).get("content", "")
            self._json(
                {
                    "content": content,
                    "raw": parsed,
                    "meta": {
                        "context_chars": _messages_char_count(outgoing_messages),
                        "max_context_chars": MAX_CONTEXT_CHARS,
                        "profile_compacted": profile_compacted,
                        "conversation_compacted": conversation_compacted,
                        "recent_message_count": RECENT_MESSAGE_COUNT,
                        "forced_tool_used": forced_tool_used,
                    },
                }
            )

        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            self._json(
                {
                    "error": "ollama_http_error",
                    "status": exc.code,
                    "detail": detail,
                },
                status=HTTPStatus.BAD_GATEWAY,
            )
        except error.URLError as exc:
            self._json(
                {
                    "error": "ollama_unreachable",
                    "detail": str(exc.reason),
                },
                status=HTTPStatus.BAD_GATEWAY,
            )
        except Exception as exc:  # pylint: disable=broad-except
            self._json(
                {"error": "server_error", "detail": str(exc)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return
        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[chat-ui] {self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Chat UI running on http://{HOST}:{PORT}")
    print(f"Using Ollama endpoint: {OLLAMA_URL}")
    print(f"Default model: {DEFAULT_MODEL}")
    server.serve_forever()
