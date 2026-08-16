import os
import json
import datetime
from typing import Dict, Any, List, Optional
from nexa.core.events.bus import PipelineBus, EventContext
from nexa.core.models.enums import EventPriority
from nexa.core.agent.tools.models import ToolMetadata

class TodoStore:
    """
    Manages persistent todos stored in .nexa/todos.json.
    """
    def __init__(self, cwd: str, bus: Optional[PipelineBus] = None, session_id: Any = 0):
        self.cwd = cwd
        self.bus = bus
        self.session_id = session_id
        self.file_path = os.path.join(self.cwd, ".nexa", "todos.json")
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._save_raw([])

    def _load_raw(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            return []
        return []

    def _save_raw(self, todos: List[Dict[str, Any]]) -> None:
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            temp_path = self.file_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(todos, f, indent=2)
            if os.path.exists(self.file_path):
                os.replace(temp_path, self.file_path)
            else:
                os.rename(temp_path, self.file_path)
        except Exception:
            pass

    def list_todos(self) -> List[Dict[str, Any]]:
        return self._load_raw()

    def add_todo(self, title: str) -> Dict[str, Any]:
        todos = self._load_raw()
        next_id = max([t.get("id", 0) for t in todos], default=0) + 1
        new_todo = {
            "id": next_id,
            "title": title,
            "status": "pending",
            "created_at": datetime.datetime.now().isoformat()
        }
        todos.append(new_todo)
        self._save_raw(todos)
        self._publish_update(todos)
        return new_todo

    def update_todo(self, todo_id: int, status: str) -> Optional[Dict[str, Any]]:
        todos = self._load_raw()
        updated = None
        for t in todos:
            if t.get("id") == todo_id:
                t["status"] = status
                t["updated_at"] = datetime.datetime.now().isoformat()
                updated = t
                break
        if updated:
            self._save_raw(todos)
            self._publish_update(todos)
        return updated

    def remove_todo(self, todo_id: int) -> bool:
        todos = self._load_raw()
        original_len = len(todos)
        todos = [t for t in todos if t.get("id") != todo_id]
        if len(todos) < original_len:
            self._save_raw(todos)
            self._publish_update(todos)
            return True
        return False

    def clear_todos(self) -> None:
        self._save_raw([])
        self._publish_update([])

    def _publish_update(self, todos: List[Dict[str, Any]]):
        if self.bus:
            try:
                self.bus.publish_async(EventContext(
                    event_name="AgentTasksUpdated",
                    timestamp=datetime.datetime.now().isoformat(),
                    source="TodoStore",
                    priority=EventPriority.NORMAL,
                    session_id=self.session_id,
                    payload={"tasks": todos}
                ))
            except Exception:
                pass


def register_todo_tools(registry, cwd: str, bus: Optional[PipelineBus] = None, session_id: Any = 0) -> TodoStore:
    """Registers LLM tools for Todo management."""
    store = TodoStore(cwd=cwd, bus=bus, session_id=session_id)

    def todo_list() -> str:
        todos = store.list_todos()
        if not todos:
            return "No todos found in project."
        lines = []
        for t in todos:
            icon = "☑" if t.get("status") == "done" else "☐"
            lines.append(f"{icon} [{t.get('id')}] {t.get('title')} ({t.get('status')})")
        return "\n".join(lines)

    def todo_add(title: str) -> str:
        if not title.strip():
            return "Error: title is required."
        item = store.add_todo(title.strip())
        return f"Todo #{item['id']} created: '{item['title']}'."

    def todo_update(id: int, status: str) -> str:
        status_clean = status.strip().lower()
        if status_clean not in ["pending", "done", "in_progress", "cancelled"]:
            return f"Error: Invalid status '{status}'. Valid: pending, in_progress, done, cancelled."
        item = store.update_todo(int(id), status_clean)
        if item:
            return f"Todo #{id} updated to status '{status_clean}'."
        return f"Error: Todo #{id} not found."

    def todo_remove(id: int) -> str:
        if store.remove_todo(int(id)):
            return f"Todo #{id} removed."
        return f"Error: Todo #{id} not found."

    registry.register(
        "todo_list",
        todo_list,
        {
            "type": "function",
            "function": {
                "name": "todo_list",
                "description": "List all active project todos and task checklists.",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        ToolMetadata(
            name="todo_list", cost=1, latency="fast", category="todo", read_only=True, priority=90, capabilities=["todo_list", "task_management"]
        )
    )

    registry.register(
        "todo_add",
        todo_add,
        {
            "type": "function",
            "function": {
                "name": "todo_add",
                "description": "Add a new task or todo item to the project checklist.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title/description of the todo task"}
                    },
                    "required": ["title"]
                }
            }
        },
        ToolMetadata(
            name="todo_add", cost=2, latency="fast", category="todo", read_only=False, priority=90, capabilities=["todo_add", "task_management"]
        )
    )

    registry.register(
        "todo_update",
        todo_update,
        {
            "type": "function",
            "function": {
                "name": "todo_update",
                "description": "Update the status of an existing todo (pending, in_progress, done, cancelled).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID of the todo"},
                        "status": {"type": "string", "description": "New status: pending, in_progress, done, cancelled"}
                    },
                    "required": ["id", "status"]
                }
            }
        },
        ToolMetadata(
            name="todo_update", cost=2, latency="fast", category="todo", read_only=False, priority=90, capabilities=["todo_update", "task_management"]
        )
    )

    return store
