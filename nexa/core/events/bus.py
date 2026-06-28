import fnmatch
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Dict, Any, Union, Tuple
import traceback

from nexa.core.models.events import EventContext
from nexa.core.events.middleware import Middleware, PropagateHalted

# Subscriber adalah Callable yang menerima EventContext
SubscriberCallable = Callable[[EventContext], None]

class PipelineBus:
    """
    Spine/Execution Bus utama Nexa.
    Mendukung pendaftaran Middleware dan Subscriber (dengan predicate/wildcard filter).
    Thread-safe menggunakan ThreadPoolExecutor untuk eksekusi async.
    """
    def __init__(self, max_workers: int = 4):
        self._middlewares: List[Middleware] = []
        # List of Tuple: (FilterStringOrCallable, SubscriberCallable)
        self._subscribers: List[Tuple[Union[str, Callable[[EventContext], bool]], SubscriberCallable]] = []
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._is_running = True

    def register_middleware(self, middleware: Middleware) -> None:
        self._middlewares.append(middleware)

    def subscribe(self, event_filter: Union[str, Callable[[EventContext], bool]], subscriber: SubscriberCallable) -> None:
        self._subscribers.append((event_filter, subscriber))

    def _should_trigger(self, event_filter: Union[str, Callable[[EventContext], bool]], context: EventContext) -> bool:
        if callable(event_filter):
            return event_filter(context)
        elif isinstance(event_filter, str):
            return fnmatch.fnmatch(context.event_name, event_filter)
        return False

    def publish(self, context: EventContext) -> None:
        if not self._is_running:
            return

        # 1. Execute Middleware: before_publish
        try:
            for mw in self._middlewares:
                mw.before_publish(context)
        except PropagateHalted:
            # Short-circuit dihentikan secara eksplisit oleh middleware (misal Security)
            return
        except Exception as e:
            # Middleware internal error
            for mw in self._middlewares:
                mw.on_error(context, e)
            return

        # 2. Dispatch to Subscribers
        for evt_filter, sub in self._subscribers:
            if self._should_trigger(evt_filter, context):
                try:
                    sub(context)
                except Exception as e:
                    # Isolasi error subscriber agar tidak menumbangkan bus
                    for mw in self._middlewares:
                        mw.on_error(context, e)

        # 3. Execute Middleware: after_publish
        try:
            for mw in self._middlewares:
                mw.after_publish(context)
        except Exception as e:
             for mw in self._middlewares:
                 mw.on_error(context, e)

    def publish_async(self, context: EventContext) -> None:
        """Melempar publish ke background thread."""
        if self._is_running:
            self._executor.submit(self.publish, context)
            
    def emit(self, context: EventContext) -> None:
        """Alias untuk publish, khusus digunakan oleh pihak eksternal (Plugin)."""
        self.publish(context)
        
    def emit_async(self, context: EventContext) -> None:
        self.publish_async(context)

    def shutdown(self, wait: bool = True) -> None:
        self._is_running = False
        self._executor.shutdown(wait=wait)
