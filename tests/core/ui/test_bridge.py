import unittest
import threading
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext
from nexa.core.models.enums import EventPriority
from nexa.ui.bridge import Bridge, BusMessage

class DummyApp:
    def __init__(self):
        self.messages = []
        self.event = threading.Event()
        
    def post_message(self, message):
        self.messages.append(message)
        self.event.set()

class TestBridge(unittest.TestCase):
    def test_bridge_subscribe(self):
        bus = PipelineBus(max_workers=2)
        app = DummyApp()
        
        Bridge.subscribe(bus, "AIToken", app)
        
        ctx = EventContext(
            event_name="AIToken",
            timestamp="2026-08-08",
            source="test",
            priority=EventPriority.NORMAL,
            session_id="123",
            payload={"token": "hello"}
        )
        
        bus.publish_async(ctx)
        
        # Wait for message to arrive
        app.event.wait(timeout=2.0)
        
        self.assertEqual(len(app.messages), 1)
        self.assertIsInstance(app.messages[0], BusMessage)
        self.assertEqual(app.messages[0].event_context.payload["token"], "hello")
        
        bus.shutdown()

if __name__ == "__main__":
    unittest.main()
