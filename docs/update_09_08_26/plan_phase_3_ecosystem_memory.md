# Phase 3: Ecosystem, Memory & Advanced Integrations

**Status**: Planned / Not Implemented
**Dependency**: Requires Phase 1 and Phase 2.
**Goal**: Elevate Nexa from a single-task agent to a context-aware, highly configurable software engineering companion.

## 1. Architectural Changes

### 1.1 Project-Specific Context (`AGENTS.md`)
Unlike a generic AI, a software engineering agent must adhere to project-specific coding standards (e.g., "Use Tailwind", "Don't use classes", "Tests go in /spec").
- **Implementation**: During session initialization in `NexaAgentRuntime`, the system automatically looks for `AGENTS.md` or `.nexa/instructions.md` in the project root.
- **Integration**: The contents of this file are perpetually injected into the `System Prompt` of the `AILoopEngine`.

### 1.2 Granular Permission System
Currently, `BeforeApproval` halts execution for the entire plan. With an iterative loop, asking for permission on every single tool call (e.g., `list_directory`) is terrible UX.
- **Implementation**: Create `nexa/config/permissions.json` (or similar).
- **Rules Engine**:
  - `list_directory`, `read_file`, `search`: **Auto-Allow** (No modal).
  - `write_file`, `edit_file_content`: **Ask** (Modal pop-up).
  - `run_bash_command`: **Ask** (Modal pop-up).
  - Admins can configure these rules via CLI or a configuration file.

### 1.3 Self-Managed Task/Todo System
The right panel (`#status-panel`) currently displays static todos derived from the initial plan. In an autonomous loop, the agent should manage its own state.
- **Implementation**: Create a `manage_tasks` tool.
- **Arguments**: `action` (add, complete, remove), `task_id`, `description`.
- **Integration**: When the LLM calls this tool, it updates the `StatusPanel` UI dynamically. This gives the agent a "scratchpad" to keep track of complex multi-step refactors without losing context.

## 2. Verifiability (AI Checklist)
- [ ] Agent automatically reads and obeys `AGENTS.md` instructions.
- [ ] The TUI Approval Modal only triggers for tools flagged as "Ask" (write/bash), bypassing read-only tools automatically.
- [ ] The agent can add and check off items in the TUI Status Panel dynamically using the `manage_tasks` tool.
