import unittest

from tools import youtube_recommender


class YouTubeRecommenderIntegrationTests(unittest.TestCase):
    def test_extract_direct_links_from_youtube_search(self):
        search_url = "https://www.youtube.com/results?search_query=multiplication+3x3"
        links = youtube_recommender._extract_direct_links_from_youtube_search(search_url, 5)  # noqa: SLF001
        self.assertGreaterEqual(len(links), 1)
        self.assertTrue(links[0]["url"].startswith("https://www.youtube.com/watch?v="))

    def test_recommend_youtube_videos_returns_results(self):
        result = youtube_recommender.recommend_youtube_videos({"topic": "multiplication 3x3", "max_results": 5})
        self.assertIn("fallback_search_url", result)
        self.assertGreaterEqual(len(result.get("recommendations", [])), 1)


if __name__ == "__main__":
    unittest.main()
