# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- OpenCode-parity slash commands: /connect /models /init /editor /themes /mode /details /thinking /rename /export /copy /compact /share /unshare /context /agents /undo /redo /timeline /skills /variants /mcps
- Slash dispatch registry (`SLASH_DISPATCH`) as single source of truth + dispatch integrity test
- Live UI theme application (on_mount + /themes modal) with `dark` → `textual-dark` mapping
- AGENTS.md scaffolding via /init and AGENTS.md instructions injection into system prompt
### Changed
- Refactored `command_handler` to registry-based dispatch (no more if/elif chains)
- Redo stack persisted to `.nexa/undo_stack.json` (bounded to 20 items)
- `/timeline` now reads `EventContext.payload` with correct token keys
### Fixed
- /editor now dispatches to external editor handler (was dead mapping)
- /redo restores messages (undo now pushes a snapshot to the redo stack)
- Removed dead stub branch for /skills /variants /mcps /timeline

## [1.0.0] - 2026-08-12
### Added
- Autonomous AI Agent with iterative loop engine
- TUI interactive shell using Textual
- Nexa command line interface for scaffolding (Django, Flutter, PHP)
- Semantic indexing and workspace caching
- Verification and approval gates for safe execution
- Project planning, cognitive clarification, and problem-solving memory

### Changed
- Refactored CLI help system and command dispatching to use a central registry.
- Moved all top-level AI commands (scan, plan, tree, etc.) into the `nexa ai <command>` namespace.

### Fixed
- Fixed packaging issue (missing templates in PyPI package)
- Fixed `nexa help` crashing due to `UnicodeEncodeError` on Windows
- Fixed `nexa plan` crashing due to outdated imports
- Cleaned up experimental and dummy scripts
- Fixed sqlite DeprecationWarning for Python 3.12+
