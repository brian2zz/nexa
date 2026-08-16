import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Optional
from nexa.core.agent.tools.models import ToolMetadata


class _TextExtractor(HTMLParser):
    """Extracts visible text from raw HTML without external dependencies."""

    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg", "head"):
            self._skip += 1
        if tag in ("p", "br", "div", "li", "h1", "h2", "h3", "tr"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg", "head") and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip == 0:
            self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts)
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def _http_get(url: str, timeout: int = 15) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "NexaAI/1.0 (+https://github.com/anomalyco/nexa)",
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


class WebTool:
    """
    Provides read-only web capabilities: fetch a URL or search the web.
    No API keys required.
    """

    def web_fetch(self, url: str, max_chars: int = 12000) -> str:
        """
        Fetch a URL and return its readable text content.
        """
        try:
            html = _http_get(url)
        except Exception as e:
            return f"Error fetching URL: {e}"

        parser = _TextExtractor()
        parser.feed(html)
        text = parser.text()

        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""

        result = f"URL: {url}\n"
        if title:
            result += f"Title: {title}\n"
        result += f"Content ({len(text)} chars):\n{text}"

        if len(result) > max_chars:
            result = result[:max_chars] + "\n...[truncated]"
        return result

    def web_search(self, query: str, num_results: int = 5) -> str:
        """
        Search the web for the given query and return the top results with snippets.
        """
        try:
            num_results = max(1, min(int(num_results), 10))
        except Exception:
            num_results = 5

        search_url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        try:
            html = _http_get(search_url)
        except Exception as e:
            return f"Error performing web search: {e}"

        results = []
        for match in re.finditer(
            r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
            html,
            re.IGNORECASE | re.DOTALL,
        ):
            href, title_html, snippet_html = match.groups()
            parser = _TextExtractor()
            parser.feed(title_html)
            title = parser.text().strip()
            parser2 = _TextExtractor()
            parser2.feed(snippet_html)
            snippet = parser2.text().strip()
            results.append({"title": title, "url": href, "snippet": snippet})
            if len(results) >= num_results:
                break

        if not results:
            return f"No results found for: {query}"

        lines = [f"Web search results for: {query}", ""]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet']}")
        return "\n".join(lines)


def register_web_tools(registry):
    """
    Registers read-only web tools (web_fetch, web_search) to the registry.
    """
    web = WebTool()

    registry.register(
        name="web_fetch",
        func=web.web_fetch,
        schema={
            "type": "function",
            "function": {
                "name": "web_fetch",
                "description": "Fetch the content of a given URL and return its readable text. Use this to read web pages, documentation, or raw URLs during research.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The fully-formed URL to fetch (e.g. 'https://docs.python.org/3/library/json.html')."
                        },
                        "max_chars": {
                            "type": "integer",
                            "description": "Optional maximum characters to return. Default is 12000."
                        }
                    },
                    "required": ["url"]
                }
            }
        },
        metadata=ToolMetadata(
            name="web_fetch", cost=20, latency="medium", category="web", read_only=True, capabilities=["web", "fetch"], priority=40
        )
    )

    registry.register(
        name="web_search",
        func=web.web_search,
        schema={
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for a query and return the top result titles, URLs, and snippets. Use this to research topics, find documentation, or look up current information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query."
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Optional number of results to return (1-10). Default is 5."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        metadata=ToolMetadata(
            name="web_search", cost=15, latency="medium", category="web", read_only=True, capabilities=["web", "search"], priority=40
        )
    )

    return web
