import unittest
import time
from nexa.core.events.bus import PipelineBus
from nexa.core.events.middleware import Middleware, PropagateHalted
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority

class SecurityMiddlewareMock(Middleware):
    def __init__(self):
        self.before_called = 0
        
    def before_publish(self, context: EventContext) -> None:
        self.before_called += 1
        if context.event_name == "MALICIOUS_EVENT":
            raise PropagateHalted("Blocked by security middleware")

    def after_publish(self, context: EventContext) -> None:
        pass

    def on_error(self, context: EventContext, error: Exception) -> None:
        pass

class TestPipelineBus(unittest.TestCase):
    def setUp(self):
        self.bus = PipelineBus(max_workers=2)

    def tearDown(self):
        self.bus.shutdown(wait=True)

    def test_publish_and_subscribe(self):
        received_events = []
        
        def subscriber(ctx: EventContext):
            received_events.append(ctx.event_name)

        self.bus.subscribe("*", subscriber)
        
        ctx = EventContext(
            event_name="BeforePatch",
            timestamp="2026-06-28T00:00:00",
            source="TestEngine",
            priority=EventPriority.NORMAL,
            session_id="session-123"
        )
        
        self.bus.publish(ctx)
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0], "BeforePatch")

    def test_middleware_short_circuit(self):
        sec_mw = SecurityMiddlewareMock()
        self.bus.register_middleware(sec_mw)
        
        received_events = []
        def subscriber(ctx: EventContext):
            received_events.append(ctx.event_name)
            
        self.bus.subscribe("*", subscriber)
        
        # Event normal, harus diteruskan
        ctx1 = EventContext(
            event_name="NORMAL_EVENT",
            timestamp="2026-06-28T00:00:00",
            source="TestEngine",
            priority=EventPriority.NORMAL,
            session_id="session-123"
        )
        self.bus.publish(ctx1)
        self.assertEqual(len(received_events), 1)
        self.assertEqual(sec_mw.before_called, 1)

        # Event malicious, harus diblok
        ctx2 = EventContext(
            event_name="MALICIOUS_EVENT",
            timestamp="2026-06-28T00:00:00",
            source="Hacker",
            priority=EventPriority.HIGH,
            session_id="session-123"
        )
        self.bus.publish(ctx2)
        # Tidak bertambah karena di-short-circuit
        self.assertEqual(len(received_events), 1)
        self.assertEqual(sec_mw.before_called, 2)

    def test_predicate_filter(self):
        received = []
        def subscriber(ctx: EventContext):
            received.append(ctx.event_name)
            
        # Hanya tangkap yang source == "Admin"
        self.bus.subscribe(lambda ctx: ctx.source == "Admin", subscriber)
        
        ctx1 = EventContext(event_name="E1", timestamp="t", source="User", priority=EventPriority.NORMAL, session_id="s")
        ctx2 = EventContext(event_name="E2", timestamp="t", source="Admin", priority=EventPriority.NORMAL, session_id="s")
        
        self.bus.publish(ctx1)
        self.bus.publish(ctx2)
        
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0], "E2")

if __name__ == '__main__':
    unittest.main()
