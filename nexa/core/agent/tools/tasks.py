import json
from typing import Dict, Any, List
from nexa.core.events.bus import PipelineBus, EventContext
from nexa.core.models.enums import EventPriority
import datetime

class TaskTool:
    """
    Allows the agent to manage its own todo list during long-running sessions.
    The list is displayed in the TUI's Status Panel.
    """
    def __init__(self, bus: PipelineBus = None, session_id: int = 0):
        self.bus = bus
        self.session_id = session_id
        # State of tasks
        self.tasks: List[Dict[str, Any]] = []
        self._next_id = 1

    def manage_tasks(self, action: str, title: str = "", task_id: int = -1) -> str:
        """
        Agent calls this to add, complete, or remove tasks.
        """
        if action == "add":
            if not title:
                return "Error: title is required for action 'add'."
            task = {"id": self._next_id, "title": title, "status": "pending"}
            self.tasks.append(task)
            self._next_id += 1
            self._publish_update()
            return f"Task added with ID {task['id']}."
            
        elif action == "complete":
            if task_id <= 0:
                return "Error: task_id is required for action 'complete'."
            for t in self.tasks:
                if t["id"] == task_id:
                    t["status"] = "done"
                    self._publish_update()
                    return f"Task {task_id} marked as done."
            return f"Error: Task {task_id} not found."
            
        elif action == "remove":
            if task_id <= 0:
                return "Error: task_id is required for action 'remove'."
            original_len = len(self.tasks)
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            if len(self.tasks) < original_len:
                self._publish_update()
                return f"Task {task_id} removed."
            return f"Error: Task {task_id} not found."
            
        elif action == "list":
            if not self.tasks:
                return "No tasks found."
            lines = []
            for t in self.tasks:
                status_icon = "☑" if t["status"] == "done" else "☐"
                lines.append(f"{status_icon} [{t['id']}] {t['title']}")
            return "\n".join(lines)
            
        return f"Error: unknown action '{action}'. Valid actions are 'add', 'complete', 'remove', 'list'."

    def _publish_update(self):
        if self.bus:
            self.bus.publish_async(EventContext(
                event_name="AgentTasksUpdated",
                timestamp=datetime.datetime.now().isoformat(),
                source="TaskTool",
                priority=EventPriority.NORMAL,
                session_id=self.session_id,
                payload={"tasks": self.tasks}
            ))
