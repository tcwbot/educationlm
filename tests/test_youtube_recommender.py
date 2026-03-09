import unittest
from unittest.mock import patch

from tools import youtube_recommender


class _FakeResponse:
    def __init__(self, body: str, status: int = 200):
        self._body = body.encode("utf-8")
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class YouTubeRecommenderTests(unittest.TestCase):
    def test_derive_topic_handles_common_prompt_noise(self):
        topic = youtube_recommender.derive_topic_from_text("can you recommend a youtube video multiplication 3x3?")
        self.assertEqual(topic, "multiplication 3x3")

    def test_returns_direct_links_from_youtube_when_ddg_has_no_matches(self):
        def fake_urlopen(req, timeout=20):
            url = req.full_url
            if "duckduckgo.com" in url:
                return _FakeResponse("<html><body>no result links</body></html>")
            if "youtube.com/results" in url:
                html = (
                    'var ytInitialData = {"contents":{"videoRenderer":{"videoId":"abcdEFGHijk",'
                    '"title":{"runs":[{"text":"Multiply 3x3 Fast"}]}}}};'
                    '<a href="/watch?v=abcdEFGHijk">v1</a>'
                    '<a href="/watch?v=abcdEFGHijk">dup</a>'
                    '<a href="/watch?v=lmnoPQRSTuv">v2</a>'
                )
                return _FakeResponse(html)
            raise AssertionError(f"Unexpected URL: {url}")

        with patch("tools.youtube_recommender.request.urlopen", side_effect=fake_urlopen):
            result = youtube_recommender.recommend_youtube_videos({"topic": "multiplication 3x3", "max_results": 3})

        self.assertGreaterEqual(len(result["recommendations"]), 2)
        self.assertEqual(result["recommendations"][0]["title"], "Multiply 3x3 Fast")
        self.assertIn("youtube.com/watch?v=abcdEFGHijk", result["recommendations"][0]["url"])
        self.assertIn("parsed from YouTube search results", result.get("note", ""))

    def test_ddg_fetch_failure_still_falls_back_to_youtube_search_links(self):
        def fake_urlopen(req, timeout=20):
            url = req.full_url
            if "duckduckgo.com" in url:
                raise RuntimeError("ddg blocked")
            if "youtube.com/results" in url:
                return _FakeResponse('<a href="/watch?v=ZyxWVutsRqp">v1</a>')
            raise AssertionError(f"Unexpected URL: {url}")

        with patch("tools.youtube_recommender.request.urlopen", side_effect=fake_urlopen):
            result = youtube_recommender.recommend_youtube_videos({"topic": "multiplication 3x3", "max_results": 2})

        self.assertEqual(len(result["recommendations"]), 1)
        self.assertEqual(result["recommendations"][0]["url"], "https://www.youtube.com/watch?v=ZyxWVutsRqp")
        self.assertIn("DuckDuckGo fetch issue", result.get("note", ""))


if __name__ == "__main__":
    unittest.main()
