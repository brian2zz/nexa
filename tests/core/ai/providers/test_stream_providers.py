import unittest
import json
from unittest.mock import patch

from nexa.core.ai.providers.ollama import OllamaProvider
from nexa.core.ai.providers.groq import GroqProvider
from nexa.core.ai.providers.deepseek import DeepSeekProvider
from nexa.core.ai.providers.gemini import GeminiProvider

MESSAGES = [{"role": "user", "content": "analyze"}]


class FakeResponse:
    """Minimal requests.Response stand-in exposing iter_lines() and context manager."""

    def __init__(self, lines, status_code=200):
        self._lines = [l.encode("utf-8") for l in lines]
        self.status_code = status_code

    def raise_for_status(self):
        pass

    def iter_lines(self):
        return iter(self._lines)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class TestOllamaStream(unittest.TestCase):
    def test_stream_parses_ollama_chunks(self):
        provider = OllamaProvider()
        lines = [
            '{"message": {"content": "Hello "}}',
            '{"message": {"content": "world"}}',
            '{"done": true}',
        ]
        with patch("requests.post", return_value=FakeResponse(lines)):
            chunks = list(provider.stream(MESSAGES))
        self.assertEqual("".join(chunks), "Hello world")


class TestGroqStream(unittest.TestCase):
    def _provider(self):
        with patch("nexa.config.Config.get", side_effect=lambda k, d=None: {
            "groq.api_key": "test-key",
            "groq.host": "https://api.groq.com/openai/v1",
            "groq.model": "llama-3.1-8b-instant",
        }.get(k, d)):
            return GroqProvider()

    def test_stream_parses_sse_chunks(self):
        provider = self._provider()
        lines = [
            'data: {"choices": [{"delta": {"content": "Hi"}}]}',
            'data: {"choices": [{"delta": {"content": " there"}}]}',
            'data: [DONE]',
        ]
        with patch("requests.post", return_value=FakeResponse(lines)):
            chunks = list(provider.stream(MESSAGES))
        self.assertEqual("".join(chunks), "Hi there")

    def test_stream_skips_empty_delta(self):
        provider = self._provider()
        lines = [
            'data: {"choices": [{"delta": {"role": "assistant"}}]}',
            'data: {"choices": [{"delta": {"content": "ok"}}]}',
            'data: [DONE]',
        ]
        with patch("requests.post", return_value=FakeResponse(lines)):
            chunks = list(provider.stream(MESSAGES))
        self.assertEqual("".join(chunks), "ok")


class TestDeepSeekStream(unittest.TestCase):
    def _provider(self):
        with patch("nexa.config.Config.get", side_effect=lambda k, d=None: {
            "deepseek.api_key": "test-key",
            "deepseek.host": "https://api.deepseek.com",
            "deepseek.model": "deepseek-chat",
        }.get(k, d)):
            return DeepSeekProvider()

    def test_stream_parses_sse_chunks(self):
        provider = self._provider()
        lines = [
            'data: {"choices": [{"delta": {"content": "Plan:"}}]}',
            'data: {"choices": [{"delta": {"content": " step1"}}]}',
            'data: [DONE]',
        ]
        with patch("requests.post", return_value=FakeResponse(lines)):
            chunks = list(provider.stream(MESSAGES))
        self.assertEqual("".join(chunks), "Plan: step1")


class TestGeminiStream(unittest.TestCase):
    def _provider(self):
        with patch("nexa.config.Config.get", side_effect=lambda k, d=None: {
            "gemini.api_key": "test-key",
            "gemini.model": "gemini-2.5-flash",
        }.get(k, d)):
            return GeminiProvider()

    def test_stream_parses_candidates_parts(self):
        provider = self._provider()
        lines = [
            'data: {"candidates": [{"content": {"parts": [{"text": "one"}]}}]}',
            'data: {"candidates": [{"content": {"parts": [{"text": "two"}]}}]}',
        ]
        with patch("requests.post", return_value=FakeResponse(lines)):
            chunks = list(provider.stream(MESSAGES))
        self.assertEqual("".join(chunks), "onetwo")

    def test_stream_skips_part_without_text(self):
        provider = self._provider()
        lines = [
            'data: {"candidates": [{"content": {"parts": [{}]}}]}',
            'data: {"candidates": [{"content": {"parts": [{"text": "x"}]}}]}',
        ]
        with patch("requests.post", return_value=FakeResponse(lines)):
            chunks = list(provider.stream(MESSAGES))
        self.assertEqual("".join(chunks), "x")


if __name__ == "__main__":
    unittest.main()
