# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
