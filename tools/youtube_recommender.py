"""YouTube recommender tool for tutoring resource discovery."""

from __future__ import annotations

import json
import re
import ssl
from urllib import error, parse, request

TOOL_NAME = "recommend_youtube_videos"
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": (
            "Recommend YouTube videos for a learning topic. "
            "Use this when the student asks for additional explanations, examples, or references."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Primary concept the student wants to learn.",
                },
                "learning_goal": {
                    "type": "string",
                    "description": "Specific objective, like exam prep or project help.",
                },
                "learner_level": {
                    "type": "string",
                    "enum": ["beginner", "intermediate", "advanced"],
                    "description": "Estimated student level.",
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 8,
                    "description": "Number of recommendations to return.",
                },
            },
            "required": ["topic"],
        },
    },
}


def _urlopen_with_ssl_fallback(req: request.Request, timeout: int):
    try:
        return request.urlopen(req, timeout=timeout)
    except error.URLError as exc:
        if isinstance(exc.reason, ssl.SSLCertVerificationError):
            insecure_context = ssl._create_unverified_context()
            return request.urlopen(req, timeout=timeout, context=insecure_context)
        raise


def _decode_duckduckgo_url(raw_href: str) -> str:
    if not raw_href:
        return ""
    if raw_href.startswith("//"):
        raw_href = f"https:{raw_href}"
    parsed = parse.urlparse(raw_href)
    qs = parse.parse_qs(parsed.query)
    if "uddg" in qs and qs["uddg"]:
        return parse.unquote(qs["uddg"][0])
    return raw_href


def _extract_video_id(url: str) -> str:
    parsed = parse.urlparse(url)
    host = parsed.netloc.lower()
    if "youtu.be" in host:
        return parsed.path.strip("/").split("/")[0]
    qs = parse.parse_qs(parsed.query)
    if "v" in qs and qs["v"]:
        return qs["v"][0]
    return ""


def _canonical_youtube_watch_url(url: str) -> str:
    video_id = _extract_video_id(url)
    if not video_id:
        return ""
    return f"https://www.youtube.com/watch?v={video_id}"


def _youtube_url_is_reachable(url: str) -> bool:
    canonical = _canonical_youtube_watch_url(url)
    if not canonical:
        return False
    oembed = f"https://www.youtube.com/oembed?url={parse.quote(canonical, safe=':/?=&')}&format=json"
    req = request.Request(
        oembed,
        headers={"User-Agent": "Mozilla/5.0"},
        method="GET",
    )
    try:
        with _urlopen_with_ssl_fallback(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except Exception:  # pylint: disable=broad-except
        return False


def _extract_json_object(text: str, start: int) -> str:
    depth = 0
    in_string = False
    escape = False
    obj_start = -1
    for idx in range(start, len(text)):
        ch = text[idx]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            if depth == 0:
                obj_start = idx
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and obj_start >= 0:
                    return text[obj_start : idx + 1]
    return ""


def _extract_video_titles_from_youtube_html(html: str) -> dict[str, str]:
    markers = ("var ytInitialData =", 'window["ytInitialData"] =')
    initial_data = None
    for marker in markers:
        marker_pos = html.find(marker)
        if marker_pos < 0:
            continue
        json_blob = _extract_json_object(html, marker_pos + len(marker))
        if not json_blob:
            continue
        try:
            initial_data = json.loads(json_blob)
            break
        except json.JSONDecodeError:
            continue
    if not isinstance(initial_data, dict):
        return {}

    titles: dict[str, str] = {}

    def walk(node):
        if isinstance(node, dict):
            video = node.get("videoRenderer")
            if isinstance(video, dict):
                video_id = str(video.get("videoId") or "").strip()
                title_obj = video.get("title") or {}
                text = ""
                if isinstance(title_obj, dict):
                    if "simpleText" in title_obj:
                        text = str(title_obj.get("simpleText") or "").strip()
                    elif isinstance(title_obj.get("runs"), list) and title_obj["runs"]:
                        text = str(title_obj["runs"][0].get("text") or "").strip()
                if video_id and text and video_id not in titles:
                    titles[video_id] = text
            for value in node.values():
                walk(value)
            return
        if isinstance(node, list):
            for item in node:
                walk(item)

    walk(initial_data)
    return titles


def _extract_direct_links_from_youtube_search(youtube_search_url: str, max_results: int) -> list[dict]:
    req = request.Request(
        youtube_search_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
            )
        },
        method="GET",
    )
    with _urlopen_with_ssl_fallback(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    title_map = _extract_video_titles_from_youtube_html(html)

    # YouTube HTML often embeds repeated /watch?v=<id> links.
    ids = re.findall(r"/watch\?v=([A-Za-z0-9_-]{11})", html)
    unique_ids: list[str] = []
    seen_ids = set()
    for video_id in ids:
        if video_id in seen_ids:
            continue
        seen_ids.add(video_id)
        unique_ids.append(video_id)
        if len(unique_ids) >= max_results:
            break

    return [
        {
            "title": title_map.get(video_id) or f"YouTube result {idx}",
            "url": f"https://www.youtube.com/watch?v={video_id}",
        }
        for idx, video_id in enumerate(unique_ids, start=1)
    ]


def looks_like_youtube_request(text: str) -> bool:
    t = text.lower()
    return bool(
        re.search(r"\b(youtube|yt|video|videos|watch|tutorial|recommend)\b", t)
        and re.search(r"\b(learn|understand|help|explain|study|practice|resource|resources)\b", t)
        or "youtube" in t
    )


def derive_topic_from_text(text: str) -> str:
    normalized = re.sub(r"(?i)\b(re+co?mm?e?n+d+|recomend|reccomend)\b", "recommend", text)
    cleaned = re.sub(
        (
            r"(?i)\b("
            r"can|could|would|you|please|recommend|youtube|videos?|watch|tutorials?|"
            r"for|me|us|to|learn|help|explain|study|practice|resource|resources|"
            r"i|need|want|looking|show|find|get|a|an|the|about|on"
            r")\b"
        ),
        " ",
        normalized,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,!?:;")
    if len(cleaned) < 3:
        return "general study topic"
    return cleaned


def recommend_youtube_videos(args: dict) -> dict:
    topic = (args.get("topic") or "").strip()
    learning_goal = (args.get("learning_goal") or "").strip()
    learner_level = (args.get("learner_level") or "beginner").strip().lower()
    max_results = int(args.get("max_results") or 5)
    max_results = max(1, min(max_results, 8))

    if not topic:
        return {"error": "topic is required"}

    search_terms = f"site:youtube.com/watch {topic} {learning_goal} {learner_level} tutorial".strip()
    search_url = f"https://duckduckgo.com/html/?q={parse.quote_plus(search_terms)}"
    youtube_search_url = f"https://www.youtube.com/results?search_query={parse.quote_plus(topic)}"

    ddg_html = ""
    ddg_error = ""
    try:
        req = request.Request(
            search_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
                )
            },
            method="GET",
        )
        with _urlopen_with_ssl_fallback(req, timeout=20) as resp:
            ddg_html = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:  # pylint: disable=broad-except
        ddg_error = str(exc)

    matches = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', ddg_html, flags=re.IGNORECASE)
    recommendations = []
    fallback_candidates = []
    seen = set()
    for href, title_html in matches:
        final_url = _decode_duckduckgo_url(href)
        if "youtube.com/watch" not in final_url and "youtu.be/" not in final_url:
            continue
        clean_url = _canonical_youtube_watch_url(final_url)
        if not clean_url:
            continue
        if clean_url in seen:
            continue
        clean_title = re.sub(r"<[^>]+>", "", title_html).strip() or "YouTube video"
        fallback_candidates.append({"title": clean_title, "url": clean_url})
        if not _youtube_url_is_reachable(clean_url):
            continue
        seen.add(clean_url)
        recommendations.append({"title": clean_title, "url": clean_url})
        if len(recommendations) >= max_results:
            break

    if recommendations:
        return {
            "topic": topic,
            "learning_goal": learning_goal,
            "learner_level": learner_level,
            "recommendations": recommendations,
            "fallback_search_url": youtube_search_url,
        }

    if fallback_candidates:
        payload = {
            "topic": topic,
            "learning_goal": learning_goal,
            "learner_level": learner_level,
            "recommendations": fallback_candidates[:max_results],
            "note": "Returned unverified direct links because verification failed.",
            "fallback_search_url": youtube_search_url,
        }
        if ddg_error:
            payload["note"] = f'{payload["note"]} DuckDuckGo fetch issue: {ddg_error}'
        return payload

    try:
        direct_candidates = _extract_direct_links_from_youtube_search(youtube_search_url, max_results)
    except Exception as exc:  # pylint: disable=broad-except
        direct_candidates = []
        if not ddg_error:
            ddg_error = str(exc)

    if direct_candidates:
        payload = {
            "topic": topic,
            "learning_goal": learning_goal,
            "learner_level": learner_level,
            "recommendations": direct_candidates,
            "note": "Returned direct links parsed from YouTube search results.",
            "fallback_search_url": youtube_search_url,
        }
        if ddg_error:
            payload["note"] = f'{payload["note"]} DuckDuckGo fetch issue: {ddg_error}'
        return payload

    payload = {
        "topic": topic,
        "learning_goal": learning_goal,
        "learner_level": learner_level,
        "recommendations": [],
        "note": "No parsed results. Use the fallback YouTube search URL.",
        "fallback_search_url": youtube_search_url,
    }
    if ddg_error:
        payload["error"] = ddg_error
    return payload


def forced_youtube_content(tool_result: dict) -> str:
    recs = tool_result.get("recommendations") or []
    topic = tool_result.get("topic", "the requested topic")
    fallback = tool_result.get("fallback_search_url", "")
    if not recs:
        if fallback:
            return (
                f"I could not verify direct videos for **{topic}** right now.\n\n"
                f"Use this search link: {fallback}"
            )
        return f"I could not verify direct videos for **{topic}** right now."

    lines = [f"Recommended YouTube videos for **{topic}**:"]
    for idx, rec in enumerate(recs, start=1):
        title = rec.get("title", "Untitled")
        url = rec.get("url", "")
        lines.append(f"{idx}. [{title}]({url})")
    if fallback:
        lines.append(f"\nMore results: {fallback}")
    return "\n".join(lines)
