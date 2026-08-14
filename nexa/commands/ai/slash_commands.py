"""
Slash commands implementation for Nexa AI Shell.
Provides full parity with opencode built-in commands.
"""
import os
import sys
import datetime
from typing import Dict, Any, Tuple, List, Optional
from nexa.config import Config
from nexa.core.ai.providers.factory import ProviderFactory

# Full metadata definition for slash commands
SLASH_METADATA: List[Tuple[str, str, str]] = [
    # (command, description, category)
    ("/help", "Show available commands", "General"),
    ("/status", "Show runtime configuration & status", "General"),
    ("/exit", "Exit the AI shell (aliases: /quit, /q)", "General"),
    ("/commands", "Show available CLI commands for current project", "General"),
    ("/editor", "Open external editor (Notepad, VS Code, Vim) for long prompt", "General"),
    ("/init", "Initialize AGENTS.md guide for AI autonomy in project", "Project"),
    ("/plan", "Generate an execution plan for a goal", "Project"),
    ("/facts", "Manage persistent project facts (/facts set <k> <v>, /facts remove <k>)", "Project"),
    ("/context", "Show token usage & session context statistics", "Project"),
    ("/connect", "Composite wizard to select provider & enter API key", "Config"),
    ("/select-provider", "Switch AI Provider (ollama, deepseek, groq, gemini, mock)", "Config"),
    ("/models", "List and select models available for active provider", "Config"),
    ("/set-model", "Set active model for current provider", "Config"),
    ("/set-api-key", "Set API key for cloud providers", "Config"),
    ("/themes", "View or set UI theme (/themes <name>)", "Config"),
    ("/mode", "Switch between PLAN (read-only grill-me) and BUILD (write code) mode", "Config"),
    ("/details", "Toggle detailed reasoning/thought display", "Config"),
    ("/thinking", "Toggle reasoning block visibility (alias for /details)", "Config"),
    ("/new", "Start a brand new chat session (alias: /clear)", "Session"),
    ("/clear", "Clear current chat session and start new", "Session"),
    ("/history", "Show past chat session history", "Session"),
    ("/sessions", "Manage chat sessions (/sessions list, enter <id>, delete <id>)", "Session"),
    ("/load", "Load a past chat session by ID", "Session"),
    ("/rename", "Rename the current active chat session (/rename <name>)", "Session"),
    ("/export", "Export current chat history to Markdown file", "Session"),
    ("/copy", "Copy last AI response or code snippet to system clipboard (alias: Ctrl+Y)", "Session"),
    ("/compact", "Summarize and compact current session to save tokens", "Session"),
    ("/share", "Export chat session for sharing (local Markdown)", "Session"),
    ("/unshare", "Info on local export management", "Session"),
    ("/pin", "Pin last AI response or text to project memory", "Memory"),
    ("/pins", "View all pinned memory entries", "Memory"),
    ("/unpin", "Remove a pinned memory entry by ID", "Memory"),
    ("/clearpins", "Clear all pinned memory entries", "Memory"),
    ("/undo", "Revert last user message and restore previous backup", "Rollback"),
    ("/redo", "Redo last reverted action", "Rollback"),
    ("/agents", "Show Nexa agent runtime architecture and configuration", "Advanced"),
    ("/skills", "Show loaded skills (Stub: Antigravity / opencode compatible)", "Advanced"),
    ("/variants", "Manage model variants (Stub: Roadmap feature)", "Advanced"),
    ("/mcps", "Manage MCP tool servers (Stub: Roadmap feature)", "Advanced"),
    ("/timeline", "Show project event timeline (Stub: Roadmap feature)", "Advanced"),
]

SLASH_ALIASES = {
    "/q": "/exit",
    "/quit": "/exit",
    "/new": "/clear",
    "/summarize": "/compact",
    "/resume": "/sessions",
    "/continue": "/sessions",
}

class SlashCommandHandler:
    def __init__(self, runtime, cwd: str, memory_manager, facts_manager, pins_manager, framework: str):
        self.runtime = runtime
        self.cwd = cwd
        self.memory = memory_manager
        self.facts = facts_manager
        self.pins = pins_manager
        self.framework = framework

    def handle_help(self, args: str, last_ai_response: str) -> bool:
        print("\n=== Nexa AI Interactive Shell - Built-in Commands ===")
        categories = {}
        for cmd, desc, cat in SLASH_METADATA:
            categories.setdefault(cat, []).append((cmd, desc))

        for cat, items in categories.items():
            print(f"\n[{cat}]")
            for cmd, desc in items:
                print(f"  {cmd:<24}: {desc}")
        print("\nType your prompt directly to talk with AI.\n======================================================\n")
        return True

    def handle_status(self, args: str, last_ai_response: str) -> bool:
        provider = Config.get("provider", "ollama")
        model = Config.get(f"{provider}.model", "unknown")
        print("\n=== Nexa AI Status ===")
        print(f"Provider : {provider}")
        print(f"Model    : {model}")
        if provider in ["deepseek", "groq", "gemini"]:
            api_key = Config.get(f"{provider}.api_key", "")
            key_status = "SET (Hidden)" if api_key else "NOT SET"
            print(f"API Key  : {key_status}")
        elif provider == "ollama":
            host = Config.get("ollama.host", "http://localhost:11434")
            print(f"Host     : {host}")
        print(f"Session  : {self.runtime.session_id}")
        print(f"Details  : {'ON' if Config.get('ui.details', True) else 'OFF'}")
        print("======================\n")
        return True

    def handle_exit(self, args: str, last_ai_response: str) -> bool:
        print("Exiting Nexa AI Shell.")
        return False

    def handle_commands(self, args: str, last_ai_response: str) -> bool:
        print(f"\n=== Available CLI Commands for {self.framework} ===")
        if "django" in self.framework.lower():
            print("  nexa run            : Run development server")
            print("  nexa new            : Create a new Django project")
            print("  nexa startapp       : Create a new Django app")
            print("  nexa make:api       : Generate DRF API boilerplate")
            print("  nexa sync           : Sync models to DB")
            print("  nexa dev            : Run dev tools")
            print("  nexa doctor         : Check project health")
        elif "nexaphp" in self.framework.lower():
            print("  nexa new            : Create a new NexaPHP project")
            print("  nexa make:module    : Create a new module")
            print("  nexa make:model     : Create a new model")
            print("  nexa make:controller: Create a new controller")
            print("  nexa run            : Run PHP built-in server")
        elif "flutter" in self.framework.lower():
            print("  nexa new            : Create a new Flutter project")
            print("  nexa create-module  : Create a new feature module")
            print("  nexa gen-model      : Generate JSON models")
            print("  nexa run            : Run Flutter app")
            print("  nexa doctor         : Check Flutter setup")
        else:
            print("  nexa create         : Create a new project (AI Scaffolding)")
            print(f"  (No specific commands detected for {self.framework})")
        print("=========================================\n")
    def handle_editor(self, args: str, last_ai_response: str) -> bool:
        import tempfile
        import subprocess
        import shutil

        editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
        if not editor:
            if sys.platform == "win32":
                editor = "notepad.exe"
            else:
                for candidate in ["nano", "vim", "vi"]:
                    if shutil.which(candidate):
                        editor = candidate
                        break
                if not editor:
                    editor = "nano"

        try:
            with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as tf:
                temp_path = tf.name

            if sys.platform == "win32":
                subprocess.run(f'{editor} "{temp_path}"', shell=True, check=False)
            else:
                subprocess.run([editor, temp_path], check=False)

            if os.path.exists(temp_path):
                with open(temp_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

                if content:
                    self.memory.save_message(self.runtime.session_id, "user", content)
                    print(f"[*] Prompt from editor saved to Session #{self.runtime.session_id}.")
                else:
                    print("[*] Editor content was empty. Cancelled.")
        except Exception as e:
            print(f"[!] Error opening editor: {e}")
        return True

    def handle_init(self, args: str, last_ai_response: str) -> bool:
        agents_file = os.path.join(self.cwd, "AGENTS.md")
        if os.path.exists(agents_file):
            print(f"[*] AGENTS.md already exists at {agents_file}")
            return True

        content = f"""# Project Autonomous Guidelines: {os.path.basename(self.cwd)}

## Framework & Environment
- Primary Framework: {self.framework}
- Created At: {datetime.date.today()}

## Coding Standards & Conventions
1. Always maintain modular and clean architecture.
2. Follow strict linting, type-hinting, and error handling rules.
3. Write unit tests for every critical change.

## Verification Workflow
- Run tests: `pytest` / `npm test` / `flutter test`
"""
        with open(agents_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[✓] Created {agents_file} with autonomous project instructions.")
        return True

    def handle_connect(self, args: str, last_ai_response: str) -> bool:
        parts = args.split()
        if len(parts) >= 1:
            prov = parts[0].lower()
            key = parts[1] if len(parts) > 1 else ""
            Config.set("provider", prov)
            if key:
                Config.set(f"{prov}.api_key", key)
            print(f"[✓] Connected to provider: {prov}")
            return True

        print("\n=== Connect to AI Provider ===")
        print("1. ollama (Local)")
        print("2. deepseek (Cloud)")
        print("3. groq (Cloud)")
        print("4. gemini (Cloud)")
        print("5. mock (Testing)")
        choice = input("Select provider (1-5 or name): ").strip().lower()
        mapping = {"1": "ollama", "2": "deepseek", "3": "groq", "4": "gemini", "5": "mock"}
        prov = mapping.get(choice, choice)
        if prov in ["ollama", "deepseek", "groq", "gemini", "mock"]:
            Config.set("provider", prov)
            if prov in ["deepseek", "groq", "gemini"]:
                import getpass
                key = getpass.getpass(f"Enter API Key for {prov} (leave empty to keep current): ").strip()
                if key:
                    Config.set(f"{prov}.api_key", key)
            print(f"[✓] Successfully connected to {prov}.")
        else:
            print("[!] Invalid provider.")
        return True

    def handle_models(self, args: str, last_ai_response: str) -> bool:
        provider = Config.get("provider", "ollama").lower()
        model_presets = {
            "ollama": ["llama3.1", "gemma:2b", "qwen3:14b", "deepseek-coder", "phi3", "mistral"],
            "deepseek": ["deepseek-chat", "deepseek-coder"],
            "groq": ["llama3-70b-8192", "mixtral-8x7b-32768"],
            "gemini": ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"],
            "mock": ["mock-model"]
        }
        avail = model_presets.get(provider, ["default"])
        if args.strip():
            target_model = args.strip()
            Config.set(f"{provider}.model", target_model)
            print(f"[✓] Active model for {provider} set to `{target_model}`")
            return True

        curr = Config.get(f"{provider}.model", "unknown")
        print(f"\n=== Available Models for {provider} ===")
        for m in avail:
            marker = " (Active)" if m == curr else ""
            print(f"  - {m}{marker}")
        print(f"\nTo switch: /models <model_name> or /set-model <model_name>\n")
        return True

    def handle_themes(self, args: str, last_ai_response: str) -> bool:
        themes = ["textual-dark", "textual-light", "nord", "monokai", "dracula", "catppuccin"]
        if args.strip():
            t = args.strip().lower()
            Config.set("ui.theme", t)
            print(f"[✓] UI theme set to `{t}`")
            return True
        curr = Config.get("ui.theme", "textual-dark")
        print("\n=== UI Themes ===")
        for t in themes:
            marker = " (Active)" if t == curr else ""
            print(f"  - {t}{marker}")
        print("\nUsage: /themes <theme_name>\n")
        return True

    def handle_mode(self, args: str, last_ai_response: str) -> bool:
        if args.strip():
            m = args.strip().upper()
            if m in ["PLAN", "BUILD"]:
                Config.set("agent.mode", m)
                print(f"[✓] Mode switched to: {m}")
                return True
            else:
                print("Usage: /mode [PLAN | BUILD]")
                return True
        curr = Config.get("agent.mode", "PLAN").upper()
        new_mode = "BUILD" if curr == "PLAN" else "PLAN"
        Config.set("agent.mode", new_mode)
        print(f"[✓] Mode switched to: {new_mode} ({'Write & Code Editing' if new_mode == 'BUILD' else 'Read-Only Analysis / Grill-me'})")
        return True

    def handle_details(self, args: str, last_ai_response: str) -> bool:
        curr = Config.get("ui.details", True)
        new_val = not curr
        Config.set("ui.details", new_val)
        Config.set("ui.show_reasoning", new_val)
        status_str = "ENABLED" if new_val else "DISABLED"
        print(f"[*] AI Detailed reasoning/thinking output is now {status_str}.")
        return True

    def handle_rename(self, args: str, last_ai_response: str) -> bool:
        if not args.strip():
            print("Usage: /rename <new_session_name>")
            return True
        new_name = args.strip()
        if self.memory.rename_session(self.runtime.session_id, new_name):
            print(f"[✓] Session ID {self.runtime.session_id} renamed to \"{new_name}\"")
        else:
            print(f"[!] Failed to rename session ID {self.runtime.session_id}")
        return True

    def handle_export(self, args: str, last_ai_response: str) -> bool:
        messages = self.memory.load_session_messages(self.runtime.session_id, limit=500)
        if not messages:
            print("[!] No messages to export in current session.")
            return True

        exports_dir = os.path.join(self.cwd, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_{self.runtime.session_id}_{ts}.md"
        filepath = os.path.join(exports_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Nexa Chat Transcript (Session ID: {self.runtime.session_id})\n\n")
            f.write(f"- Exported At: {datetime.datetime.now().isoformat()}\n")
            f.write(f"- Project: {self.cwd}\n\n---\n\n")
            for msg in messages:
                role = msg.get("role", "").capitalize()
                content = msg.get("content", "")
                f.write(f"### {role}\n\n{content}\n\n---\n\n")

        print(f"[✓] Exported {len(messages)} messages to {filepath}")
        return True

    def handle_copy(self, args: str, last_ai_response: str) -> bool:
        import subprocess
        # Get content: from args, or last_ai_response, or last assistant message from DB
        text_to_copy = args.strip() or last_ai_response or ""
        if not text_to_copy:
            last = getattr(self.memory, "get_last_message", lambda sid: None)(self.runtime.session_id)
            if last:
                text_to_copy = last.get("content", "")

        if not text_to_copy:
            print("[!] Nothing to copy (no recent AI response found).")
            return True

        try:
            if sys.platform == "win32":
                proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                proc.communicate(input=text_to_copy.encode('utf-8'))
            else:
                proc = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                proc.communicate(input=text_to_copy.encode('utf-8'))
            print(f"[✓] Copied {len(text_to_copy)} characters to system clipboard.")
        except Exception as e:
            print(f"[!] Failed to copy to clipboard: {e}")
        return True

    def handle_share(self, args: str, last_ai_response: str) -> bool:
        print("[*] Note: Online cloud sharing is not enabled in this build. Exporting locally...")
        return self.handle_export(args, last_ai_response)

    def handle_unshare(self, args: str, last_ai_response: str) -> bool:
        print("[*] All chats and transcripts remain local on your machine in the `exports/` folder and SQLite database.")
        return True

    def handle_context(self, args: str, last_ai_response: str) -> bool:
        messages = self.memory.load_session_messages(self.runtime.session_id, limit=100)
        user_msgs = sum(1 for m in messages if m.get("role") == "user")
        ai_msgs = sum(1 for m in messages if m.get("role") == "assistant")
        total_chars = sum(len(m.get("content", "")) for m in messages)
        est_tokens = total_chars // 4

        provider = Config.get("provider", "ollama")
        model = Config.get(f"{provider}.model", "unknown")

        print("\n=== Session Context & Token Usage ===")
        print(f"Session ID     : {self.runtime.session_id}")
        print(f"Provider/Model : {provider} / {model}")
        print(f"Total Messages : {len(messages)} ({user_msgs} User, {ai_msgs} AI)")
        print(f"Approx Tokens  : ~{est_tokens} tokens cached in session")
        print(f"Project Facts  : {len(self.facts.get_all(self.cwd))} items")
        print(f"Pinned Memory  : {len(self.pins.get_all(self.cwd))} items")
        print("======================================\n")
        return True

    _redo_stack: List[Dict[str, Any]] = []

    def handle_compact(self, args: str, last_ai_response: str) -> bool:
        messages = self.memory.load_session_messages(self.runtime.session_id, limit=50)
        if len(messages) < 4:
            print("[*] Session is already short, compaction is not needed yet.")
            return True

        print("[*] Compacting chat session history...")
        conversation_dump = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        prompt_content = (
            "Summarize the key facts, tasks, and state of the following conversation briefly and clearly "
            "so context can be preserved:\n\n" + conversation_dump
        )

        try:
            provider = ProviderFactory.create()
            resp = provider.generate([
                {"role": "system", "content": "You are a concise summarizer for chat context."},
                {"role": "user", "content": prompt_content}
            ])
            summary = resp.get("content", "") if isinstance(resp, dict) else str(resp)
            # Create a clean session and insert summary
            new_session_id = self.memory.create_session(self.cwd)
            self.memory.save_message(new_session_id, "assistant", f"[Compacted Summary of Session {self.runtime.session_id}]\n{summary}")
            self.runtime.session_id = new_session_id
            print(f"[✓] Conversation compacted into new Session ID: {new_session_id}")
        except Exception as e:
            print(f"[!] Compaction failed: {e}")
        return True

    def handle_agents(self, args: str, last_ai_response: str) -> bool:
        print("\n=== Nexa Autonomous Agent Architecture ===")
        print(f"Runtime Version: 1.0.0")
        print(f"Engine Type    : Autonomous Loop Engine (Textual + Rich + PipelineBus)")
        print(f"Active Bus     : {self.runtime.bus.__class__.__name__}")
        print(f"Working Dir    : {self.cwd}")
        print(f"Session Memory : SQLite + Pinned Facts")
        print("==========================================\n")
        return True

    def handle_stub(self, feature_name: str) -> bool:
        print(f"[*] /{feature_name} is currently a planned roadmap capability in Nexa Enterprise AI.")
        return True

    def handle_undo(self, args: str, last_ai_response: str) -> bool:
        from nexa.core.pipeline.rollback.backup import BackupRollbackStrategy
        print("[*] Reverting last message & checking file restore points...")
        try:
            # Snapshot last message for redo
            last_msg = getattr(self.memory, "get_last_message", lambda sid: None)(self.runtime.session_id)
            if last_msg:
                self._redo_stack.append({"session_id": self.runtime.session_id, "message": last_msg})

            # 1. Rollback files if backup exists
            strategy = BackupRollbackStrategy(self.cwd)
            file_restored = strategy.rollback()
            
            # 2. Revert last message from memory
            msg_reverted = self.memory.delete_last_message(self.runtime.session_id)
            if msg_reverted:
                print(f"[✓] Removed last message from Session #{self.runtime.session_id}.")
            
            if file_restored:
                print("[✓] Restored files from previous execution backup.")
            elif not msg_reverted:
                print("[*] No active file backups or messages to revert.")
        except Exception as e:
            print(f"[!] Undo error: {e}")
        return True

    def handle_redo(self, args: str, last_ai_response: str) -> bool:
        if not self._redo_stack:
            print("[*] Redo stack is empty: No pending forward rollback states.")
        else:
            item = self._redo_stack.pop()
            sid = item.get("session_id")
            msg = item.get("message", {})
            if sid and msg:
                self.memory.save_message(sid, msg.get("role", "user"), msg.get("content", ""))
                print(f"[✓] Restored message ({msg.get('role')}): \"{msg.get('content', '')[:40]}\" to Session #{sid}.")
            else:
                print("[*] Reapplied redo state.")
        return True
