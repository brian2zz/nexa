# Phase 1: Autonomous Agent Loop Upgrade

**Status**: Planned / Not Implemented
**Goal**: Transform Nexa from a rigid, one-way "Planner-Executor" to a dynamic, iterative Agent Loop where the LLM can call tools, read their outputs, and decide its next action autonomously.

## 1. Architectural Changes

### 1.1 From Linear to Iterative
Currently, `nexa/commands/ai/shell.py` triggers `AIPlannerEngine.plan()`, which spits out a final plan, gets approved via `ApprovalModal`, and is executed deterministically by `ExecutionTransaction` outside the LLM's control.

**New Architecture (Agent Loop):**
```text
User Request -> Agent Engine (Loop Start)
   ^                     |
   |                     v
   |             [ LLM Thinks ]
   |                     |
   |                     v
   +------- (Output returned) <--- [ Tool Execution ]
```
- **Loop Limit:** Define a max iterations limit (e.g., `MAX_ITERATIONS = 15`) to prevent infinite looping.
- **Context Injection:** Every tool execution result MUST be appended back to the conversation memory as a `ToolResult` or `System` message so the LLM can read the outcome (e.g., reading bash errors).

### 1.2 Deprecating the Rigid `ExecutionTransaction`
The current atomic transaction (backup -> apply -> verify -> commit/rollback) limits the AI. 
**Decision:** We will **remove** the automatic, rigid `ExecutionTransaction` at the end of the pipeline. Instead, error recovery is delegated to the AI itself. If an execution fails, the LLM reads the error and fixes it in the next loop iteration.

## 2. File Implementation Plan

### `nexa/core/ai/agent_loop.py` (NEW)
Create the core loop engine `AILoopEngine`.
- **Method `run_loop(context, max_iterations=15)`:**
  1. Append user prompt to memory.
  2. `while loop_count < max_iterations:`
  3. Call LLM (predict next action/tool).
  4. If LLM returns a final response (no tools), `break` and return to user.
  5. If LLM calls a tool:
     - Check permissions (Is approval needed? Emit `BeforeApproval` event if yes).
     - Execute the tool.
     - Append tool's raw `stdout`/`stderr` back to context.
  6. Repeat.

### `nexa/commands/ai/shell.py`
- Replace `AIPlannerEngine` instantiation with `AILoopEngine`.
- Update the UI to render the agent's progress dynamically (e.g., showing a streaming log of "Agent is thinking... Agent called tool X... Agent is reading output...").

### `nexa/ui/app.py` & `nexa/core/approval/engine.py`
- Refactor `BeforeApproval` event. Currently, it approves an entire `ExecutionPlan`. It must be refactored to approve **individual tool calls** (e.g., "AI wants to run `npm install`. Approve?").
- The TUI Modal must pause the `AILoopEngine` background thread via `threading.Event().wait()` (similar to the Clarification Gate) and resume when the user clicks "Yes" or "No".

## 3. Verifiability (AI Checklist)
- [ ] `AILoopEngine` is created and can iterate multiple times per user prompt.
- [ ] Tool outputs are successfully appended back to the LLM context.
- [ ] The TUI Approval Modal now intercepts dangerous tool calls mid-loop instead of at the end of a plan.
- [ ] No infinite loops (hard stop at `MAX_ITERATIONS`).
