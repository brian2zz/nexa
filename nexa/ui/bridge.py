from typing import Union, Callable
from textual.app import App
from textual.message import Message
from nexa.core.events.bus import PipelineBus
from nexa.core.models.events import EventContext

class BusMessage(Message):
    """
    Message sent to Textual app wrapping an EventContext from PipelineBus.
    """
    def __init__(self, event_context: EventContext) -> None:
        self.event_context = event_context
        super().__init__()

class Bridge:
    """
    Bridges events from PipelineBus to Textual App safely.
    """
    @staticmethod
    def subscribe(bus: PipelineBus, event_filter: Union[str, Callable[[EventContext], bool]], app: App) -> None:
        """
        Subscribes to PipelineBus and posts BusMessage to the Textual App thread.
        """
        def handler(context: EventContext) -> None:
            # Post message to Textual's event loop
            try:
                app.post_message(BusMessage(context))
            except Exception:
                # App might be shutting down or not fully initialized
                pass
            
        bus.subscribe(event_filter, handler)
