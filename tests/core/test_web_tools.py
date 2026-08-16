import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

import nexa.core.agent.tools.web as web_mod
from nexa.core.agent.tools.registry import ToolRegistry
from nexa.core.agent.tools.web import WebTool, _TextExtractor, register_web_tools


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"<html><head><title>Test Page</title></head><body><h1>Hello Web</h1><p>Nexa fetched this.</p></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture
def local_server():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()
    server.server_close()


def test_text_extractor():
    html = "<html><head><title>x</title></head><body><p>Hello  world</p><script>var y=1;</script><p>After</p></body></html>"
    parser = _TextExtractor()
    parser.feed(html)
    text = parser.text()
    assert "Hello world" in text
    assert "After" in text
    assert "var y=1" not in text


def test_web_fetch_local(local_server):
    tool = WebTool()
    res = tool.web_fetch(local_server)
    assert "Test Page" in res
    assert "Nexa fetched this." in res


def test_web_fetch_error():
    tool = WebTool()
    res = tool.web_fetch("http://127.0.0.1:1/nonexistent")
    assert res.startswith("Error fetching URL")


def test_web_search_parses_results(monkeypatch):
    html = """
    <html><body>
    <div class="result">
      <a class="result__a" href="https://example.com/a">First Result</a>
      <a class="result__snippet" href="#">Snippet number one here.</a>
    </div>
    <div class="result">
      <a class="result__a" href="https://example.com/b">Second Result</a>
      <a class="result__snippet" href="#">Snippet number two here.</a>
    </div>
    </body></html>
    """
    monkeypatch.setattr(web_mod, "_http_get", lambda url, timeout=15: html)

    tool = WebTool()
    res = tool.web_search("python testing", num_results=5)
    assert "First Result" in res
    assert "https://example.com/a" in res
    assert "Snippet number one here." in res
    assert "Second Result" in res


def test_web_search_no_results(monkeypatch):
    monkeypatch.setattr(web_mod, "_http_get", lambda url, timeout=15: "<html><body>nothing</body></html>")
    tool = WebTool()
    res = tool.web_search("no-such-query")
    assert "No results found" in res


def test_web_tools_registered_read_only():
    registry = ToolRegistry()
    register_web_tools(registry)
    assert "web_fetch" in registry.get_all_metadata()
    assert "web_search" in registry.get_all_metadata()
    assert registry.get_metadata("web_fetch").read_only is True
    assert registry.get_metadata("web_search").read_only is True
