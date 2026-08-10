# Phase 2: Agent Toolset & Execution Capabilities

**Status**: Planned / Not Implemented
**Dependency**: Requires Phase 1 (Autonomous Agent Loop) to be completed first.
**Goal**: Equip the agent with real "write" and "execute" capabilities so it can interact with the environment dynamically.

## 1. Architectural Changes

Currently, Nexa tools in `nexa/core/agent/tools/` are entirely read-only (e.g., `FileTool.find`, `SearchTool.text`). The only write capability is a stub (`submit_execution_plan`). To achieve autonomy, the agent needs granular filesystem and terminal tools.

## 2. File Implementation Plan

### `nexa/core/agent/tools/terminal.py` (NEW)
**Bash Command Execution Tool**
- Wrap the existing `TerminalRunner` into an LLM-callable tool (`run_bash_command`).
- **Arguments**: `command` (string).
- **Behavior**: Runs the command in a subprocess, captures `stdout` and `stderr`, and returns it as a string.
- **Safety**: Apply a strict timeout (e.g., 60 seconds) to prevent hanging commands (like starting a server without daemonizing).

### `nexa/core/agent/tools/filesystem.py` (NEW/MODIFY)
Implement granular write/edit tools.
- **`write_file(filepath, content)`**: Creates or overwrites a file completely.
- **`edit_file_content(filepath, search_block, replace_block)`**: A surgical edit tool. Instead of asking the LLM to rewrite a 1000-line file, it sends a search string (exact match) and a replacement string. This saves tokens and reduces hallucination.
- **`list_directory(path)`**: To allow the agent to explore the workspace organically.

### `nexa/core/agent/tools/registry.py`
- Register these new tools into the `ToolRegistry`.
- Ensure they conform to the schema required by the underlying LLM providers (e.g., OpenAI function calling schema).

## 3. UI/UX Considerations
- When the agent calls `run_bash_command`, the TUI should echo the output into the left `#transcript` panel or the right `#process-log` so the user sees exactly what the agent is doing in real-time.

## 4. Verifiability (AI Checklist)
- [ ] `run_bash_command` is available to the LLM and returns stdout/stderr.
- [ ] `write_file` and `edit_file_content` are functional.
- [ ] The agent can successfully debug its own code (e.g., writes a broken script, runs it via bash tool, reads the error, and uses edit tool to fix it).
