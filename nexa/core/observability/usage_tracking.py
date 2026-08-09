import datetime
from typing import Callable
from nexa.core.ai.providers.base import LLMProvider
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority

class UsageTrackingProvider(LLMProvider):
    """Proxy yang membungkus provider asli dan mem-publish usage token ke bus."""

    def __init__(self, inner: LLMProvider, bus: PipelineBus,
                 session_id_fn: Callable[[], int]):
        self._inner = inner
        self._bus = bus
        self._session_id_fn = session_id_fn

    # --- delegasi ---
    def health(self) -> bool:
        return self._inner.health()

    def list_models(self):
        return self._inner.list_models()

    # --- generate: lapisi dengan pelaporan usage ---
    def generate(self, messages, temperature=0.2, tools=None):
        raw = self._inner.generate(messages, temperature=temperature, tools=tools)
        self._report(raw)
        return raw

    def stream(self, messages, temperature=0.2, tools=None):
        for chunk in self._inner.stream(messages, temperature=temperature, tools=tools):
            yield chunk

    def __getattr__(self, name):
        # pastikan method lain tetap tersedia
        return getattr(self._inner, name)

    def _report(self, raw):
        if not isinstance(raw, dict):
            return
        usage = raw.get("usage") or {}
        prompt = usage.get("prompt_eval_count", 0)
        completion = usage.get("eval_count", 0)
        if not prompt and not completion:
            return
        self._bus.publish_async(EventContext(
            event_name="TokenUsage",
            timestamp=datetime.datetime.now().isoformat(),
            source="UsageTrackingProvider",
            priority=EventPriority.NORMAL,
            session_id=self._session_id_fn(),
            payload={
                "prompt_tokens": prompt,
                "completion_tokens": completion,
            },
        ))
