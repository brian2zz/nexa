import sys
import getpass
from nexa.config import Config
from nexa.core.ai.providers.factory import ProviderFactory

from nexa.commands.ai.slash_commands import SLASH_METADATA, SLASH_ALIASES, SLASH_DISPATCH, SlashCommandHandler

def load_agents_instructions(cwd: str, max_chars: int = 8000) -> str:
    """Read the project's AGENTS.md file to inject into the system prompt."""
    import os
    path = os.path.join(cwd, "AGENTS.md")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()[:max_chars]
        except Exception:
            return ""
    return ""

def print_help():
    print("\n=== Nexa AI Interactive Shell - Built-in Commands ===")
    categories = {}
    for cmd, desc, cat in SLASH_METADATA:
        categories.setdefault(cat, []).append((cmd, desc))

    for cat, items in categories.items():
        print(f"\n[{cat}]")
        for cmd, desc in items:
            print(f"  {cmd:<20}: {desc}")
    print("\nType your prompt directly to talk with AI.\n======================================================\n")
    print("\n=== Nexa Global CLI Commands (Run outside this shell) ===")
    print("  nexa ai                  : Start this interactive AI shell")
    print("  nexa scan                : Scan project structure and vulnerabilities")
    print("  nexa tree                : Generate project directory tree")
    print("  nexa analyze             : Analyze codebase architecture")
    print("  nexa plan                : Generate a task execution plan")
    print("  nexa explain             : Explain a specific file or code snippet")
    print("  nexa create              : AI Scaffolding to create new projects")
    print("  nexa ask                 : Ask a quick question to Nexa AI")
    print("  nexa <framework>         : Framework specific commands (django/flutter/php)\n")

def show_status():
    provider = Config.get("provider")
    model_key = f"{provider}.model"
    model = Config.get(model_key, "Unknown")
    
    print("\n=== Nexa AI Status ===")
    print(f"Provider : {provider}")
    print(f"Model    : {model}")
    
    if provider in ["deepseek", "groq"]:
        api_key = Config.get(f"{provider}.api_key", "")
        key_status = "SET (Hidden)" if api_key else "NOT SET"
        print(f"API Key  : {key_status}")
    elif provider == "ollama":
        host = Config.get("ollama.host")
        print(f"Host     : {host}")
        
    print("======================\n")

def check_provider_readiness(provider_name):
    if provider_name == "deepseek":
        api_key = Config.get("deepseek.api_key", "")
        if not api_key:
            print(f"[!] API Key for DeepSeek is not set.")
            set_api_key("deepseek")
    elif provider_name == "groq":
        api_key = Config.get("groq.api_key", "")
        if not api_key:
            print(f"[!] API Key for Groq is not set.")
            set_api_key("groq")

def set_api_key(provider_name):
    import sys
    if hasattr(sys.stdout, "_app"): 
        print(f"[!] TUI Mode: Please use the Command Palette (Ctrl+K) -> /select-provider to set your API Key for {provider_name}.")
        return
        
    print(f"Please enter your API Key for {provider_name} (Input will be hidden):")
    api_key = getpass.getpass("API Key: ").strip()
    if api_key:
        Config.set(f"{provider_name}.api_key", api_key)
        print(f"[*] API Key for {provider_name} saved securely.")
    else:
        print("[!] API Key setup cancelled.")

def handle(args):
    print("Welcome to Nexa AI Interactive Shell.")
    print("Type /help for available commands or /exit to quit.\n")
    
    # Check current provider
    current_provider = Config.get("provider")
    check_provider_readiness(current_provider)
    
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import WordCompleter, NestedCompleter, PathCompleter
        from prompt_toolkit.history import InMemoryHistory
        from nexa.commands.ai.completer import NexaMentionCompleter, DynamicModelCompleter
        from nexa.core.ai.scanner.detector import ProjectDetector
        import os
        
        # Phase 2.9: Global Context Awareness
        detector = ProjectDetector()
        cwd = os.getcwd()
        proj_info = detector.detect(cwd)
        framework = proj_info.get("framework", "Unknown")
        language = proj_info.get("language", "Unknown")
        
        system_base_prompt = f"You are Nexa AI, a helpful coding assistant. You are currently running inside a {framework} ({language}) project at {cwd}."
        
        # Phase 2.10 & 2.11: Chat Memory, Facts, Pins Init
        from nexa.core.ai.memory import ChatMemoryManager
        from nexa.core.ai.memory.project_facts import ProjectFactsManager
        from nexa.core.ai.memory.pinned_memory import PinnedMemoryManager
        
        memory_manager = ChatMemoryManager()
        facts_manager = ProjectFactsManager()
        pins_manager = PinnedMemoryManager()
        last_ai_response = ""
        from nexa.core.agent.runtime import NexaAgentRuntime
        runtime = NexaAgentRuntime(cwd=cwd)
        print(f"[*] Started new chat session")

        provider_completer = WordCompleter(['ollama', 'deepseek', 'groq', 'gemini', 'mock'], ignore_case=True)
        path_completer = PathCompleter(only_directories=False, expanduser=True)
        model_completer = DynamicModelCompleter()
        
        slash_completer = NestedCompleter.from_nested_dict({
            '/help': None,
            '/status': None,
            '/connect': None,
            '/select-provider': provider_completer,
            '/models': model_completer,
            '/set-model': model_completer,
            '/set-api-key': None,
            '/dir': path_completer,
            '/explain': path_completer,
            '/history': None,
            '/load': None,
            '/clear': None,
            '/new': None,
            '/plan': None,
            '/editor': None,
            '/init': None,
            '/context': None,
            '/rename': None,
            '/export': None,
            '/compact': None,
            '/summarize': None,
            '/share': None,
            '/unshare': None,
            '/themes': None,
            '/details': None,
            '/thinking': None,
            '/facts': {
                'set': None,
                'remove': None,
            },
            '/pin': None,
            '/pins': None,
            '/unpin': None,
            '/clearpins': None,
            '/undo': None,
            '/redo': None,
            '/agents': None,
            '/skills': None,
            '/variants': None,
            '/mcps': None,
            '/timeline': None,
            '/sessions': {
                'list': None,
                'enter': None,
                'delete': None,
                'clear-all': None,
            },
            '/session': {
                'list': None,
                'enter': None,
                'delete': None,
                'clear-all': None,
            },
            '/commands': None,
            '/exit': None,
            '/quit': None,
            '/q': None,
        })
        
        # Combine slash commands with inline @ mentions
        completer = NexaMentionCompleter(slash_completer)
        
        session = PromptSession(history=InMemoryHistory(), completer=completer)
        
        def get_input():
            provider = Config.get("provider", "mock")
            model = Config.get(f"{provider}.model", "unknown")
            return session.prompt(f"Nexa>{model}> ", complete_while_typing=True).strip()
    except Exception as e:
        import traceback; traceback.print_exc()
        # Fallback if prompt_toolkit fails (e.g. NoConsoleScreenBufferError in some terminals)
        def get_input():
            provider = Config.get("provider", "mock")
            model = Config.get(f"{provider}.model", "unknown")
            return input(f"Nexa>{model}> ").strip()
            
    slash_handler = SlashCommandHandler(runtime, cwd, memory_manager, facts_manager, pins_manager, framework)

    def command_handler(cmd):
        nonlocal last_ai_response
        if not cmd:
            return True

        # Resolve aliases
        clean_cmd = cmd.strip()
        first_word = clean_cmd.split()[0].lower() if clean_cmd else ""
        if first_word in SLASH_ALIASES:
            clean_cmd = SLASH_ALIASES[first_word] + clean_cmd[len(first_word):]
            first_word = clean_cmd.split()[0].lower()

        # Handle Extended / OpenCode Parity Slash Commands via SLASH_DISPATCH registry
        entry = SLASH_DISPATCH.get(first_word)
        if entry:
            handler_name, prefix_len = entry
            handler = getattr(slash_handler, handler_name, None)
            if handler:
                return handler(clean_cmd[prefix_len:].strip(), last_ai_response)

        if first_word in ["/details", "/thinking"]:
            return slash_handler.handle_details(clean_cmd[len(first_word):].strip(), last_ai_response)
        elif clean_cmd.lower().startswith("/sessions"):
            # Normalize /sessions to /session
            clean_cmd = "/session" + clean_cmd[9:]

        cmd = clean_cmd

        if cmd.lower() in ["/exit", "/quit", "exit", "quit"]:
            print("Exiting Nexa AI Shell.")
            return False
            
        elif cmd.lower() == "/help":
            print_help()
            
        elif cmd.lower() == "/commands":
            print(f"\n=== Available CLI Commands for {framework} ===")
            if "django" in framework.lower():
                print("  nexa run            : Run development server")
                print("  nexa new            : Create a new Django project")
                print("  nexa startapp       : Create a new Django app")
                print("  nexa make:api       : Generate DRF API boilerplate")
                print("  nexa sync           : Sync models to DB")
                print("  nexa dev            : Run dev tools")
                print("  nexa doctor         : Check project health")
            elif "nexaphp" in framework.lower():
                print("  nexa new            : Create a new NexaPHP project")
                print("  nexa make:module    : Create a new module")
                print("  nexa make:model     : Create a new model")
                print("  nexa make:controller: Create a new controller")
                print("  nexa run            : Run PHP built-in server")
            elif "flutter" in framework.lower():
                print("  nexa new            : Create a new Flutter project")
                print("  nexa create-module  : Create a new feature module")
                print("  nexa gen-model      : Generate JSON models")
                print("  nexa run            : Run Flutter app")
                print("  nexa doctor         : Check Flutter setup")
            else:
                print("  nexa create         : Create a new project (AI Scaffolding)")
                print(f"  (No specific commands detected for {framework})")
            print("=========================================\n")
            
        elif cmd.lower() == "/status":
            show_status()
            
        elif cmd.lower().startswith("/select-provider"):
            parts = cmd.split()
            if len(parts) < 2:
                try:
                    from prompt_toolkit.shortcuts import radiolist_dialog
                    provider_name = radiolist_dialog(
                        title="Select AI Provider",
                        text="Choose a provider:",
                        values=[
                            ("ollama", "Ollama (Local)"),
                            ("deepseek", "DeepSeek (Cloud)"),
                            ("groq", "Groq (Cloud)"),
                            ("gemini", "Gemini (Cloud)"),
                            ("mock", "Mock (Testing)")
                        ]
                    ).run()
                    if not provider_name:
                        return True
                except Exception as e:
                    print(f"Error: {e}")
                    print("Usage: /select-provider <name> (e.g. ollama, deepseek)")
                    return True
            else:
                provider_name = parts[1].lower()
                
            if provider_name in ["deepseek", "groq", "gemini"]:
                api_key = Config.get(f"{provider_name}.api_key", "")
                if not api_key:
                    import sys
                    if not hasattr(sys.stdout, "_app"):
                        try:
                            from prompt_toolkit.shortcuts import input_dialog
                            new_key = input_dialog(
                                title=f"API Key Required",
                                text=f"Please enter your API Key for {provider_name}:",
                                password=False
                            ).run()
                            if new_key:
                                Config.set(f"{provider_name}.api_key", new_key)
                            else:
                                print("[!] API Key setup cancelled.")
                        except Exception:
                            set_api_key(provider_name)
                            
            Config.set("provider", provider_name)
            print(f"[*] Provider switched to: {provider_name}")
            check_provider_readiness(provider_name)
                
        elif cmd.lower().startswith("/set-model"):
            parts = cmd.split()
            provider = Config.get("provider", "mock")
            if len(parts) < 2:
                try:
                    from prompt_toolkit.shortcuts import radiolist_dialog
                    if provider == "ollama":
                        opts = [("llama3.1", "llama3.1"), ("gemma:2b", "gemma:2b"), ("qwen3:14b", "qwen3:14b"), ("deepseek-coder", "deepseek-coder"), ("phi3", "phi3"), ("mistral", "mistral")]
                    elif provider == "deepseek":
                        opts = [("deepseek-chat", "deepseek-chat"), ("deepseek-coder", "deepseek-coder")]
                    elif provider == "groq":
                        opts = [("llama3-70b-8192", "llama3-70b-8192"), ("mixtral-8x7b-32768", "mixtral-8x7b-32768")]
                    elif provider == "gemini":
                        opts = [("gemini-1.5-pro-latest", "gemini-1.5-pro"), ("gemini-1.5-flash-latest", "gemini-1.5-flash")]
                    else:
                        opts = [("default", "default")]

                    model_name = radiolist_dialog(
                        title=f"Select Model for {provider}",
                        text="Choose a model:",
                        values=opts
                    ).run()
                    if not model_name:
                        return True
                except Exception:
                    print("Usage: /set-model <model_name>")
                    return True
            else:
                model_name = parts[1]
                
            Config.set(f"{provider}.model", model_name)
            print(f"[*] Model for {provider} set to: {model_name}")
                
        elif cmd.lower().startswith("/set-api-key"):
            provider = Config.get("provider")
            set_api_key(provider)
            
        elif cmd.lower().startswith("/dir"):
            import os
            parts = cmd.split()
            path = parts[1] if len(parts) > 1 else "."
            if os.path.exists(path):
                if os.path.isdir(path):
                    print(f"Contents of {path}:")
                    try:
                        items = os.listdir(path)
                        for item in sorted(items):
                            if os.path.isdir(os.path.join(path, item)):
                                print(f"  📁 {item}/")
                            else:
                                print(f"  📄 {item}")
                    except Exception as e:
                        print(f"[!] Error reading directory: {e}")
                else:
                    print(f"[!] '{path}' is a file, not a directory. Use /explain to analyze a file.")
            else:
                print(f"[!] Path not found: {path}")
                
        elif cmd.lower().startswith("/explain"):
            from nexa.core.utils.extractor import CodeExtractor
            from nexa.core.utils.spinner import Spinner
            
            parts = cmd.split(maxsplit=1)
            if len(parts) < 2:
                print("Usage: /explain path/to/file.py:10-25")
                return True
                
            target = parts[1]
            extracted = CodeExtractor.parse_and_extract(target)
            
            if extracted.get('error'):
                print(f"[!] {extracted['error']}")
                return True
                
            code = extracted['code']
            file_path = extracted['file_path']
            start = extracted['start_line']
            end = extracted['end_line']
            
            prompt = (
                f"Please explain the following code from file `{file_path}` "
                f"(lines {start} to {end}):\n\n"
                f"```\n{code}\n```\n\n"
                f"Keep the explanation concise and easy to understand."
            )
            
            messages = [
                {"role": "system", "content": "You are Nexa AI, an expert coding assistant."},
                {"role": "user", "content": prompt}
            ]
            
            try:
                provider = ProviderFactory.create()
            except Exception as e:
                print(f"[!] Provider Error: {e}")
                return True
                
            with Spinner(f"Thinking ({provider.__class__.__name__})..."):
                try:
                    raw_resp = provider.generate(messages)
                    content = raw_resp.get("content", "") if isinstance(raw_resp, dict) else str(raw_resp)
                except Exception as e:
                    content = f"Error communicating with provider: {str(e)}"
                    
            CYAN = '\033[96m'
            RESET = '\033[0m'
            print(f"\n[*] Explanation for `{file_path}` ({start}-{end}):")
            print("-" * 40)
            print(f"{CYAN}{content}{RESET}")
            print("-" * 40 + "\n")
            
        elif cmd.lower().startswith("/plan "):
            goal = cmd[6:].strip()
            if not goal:
                print("Usage: /plan <your goal here>")
                return True
                
            from nexa.core.ai.planner import AIPlannerEngine, PlannerContext
            
            # Gather context
            facts = facts_manager.get_all(cwd)
            pins = pins_manager.get_all(cwd)
            past_messages = memory_manager.load_session_messages(runtime.session_id, limit=6)
            
            planner_context = PlannerContext(
                project_path=cwd,
                knowledge_context="",
                project_facts=facts,
                pinned_memory=pins,
                conversation_memory=past_messages,
                user_goal=goal
            )
            
            planner = AIPlannerEngine()
            from nexa.core.utils.spinner import Spinner
            with Spinner("Planning Execution..."):
                report = planner.plan(planner_context, session_id=runtime.session_id)
                
            if report.success:
                print("\n" + report.to_markdown() + "\n")
            else:
                print(f"\n[!] Planning Failed: {report.error_message}\n")
            
        elif cmd.lower().startswith("/facts"):
            parts = cmd.split(maxsplit=3)
            if len(parts) == 1:
                facts = facts_manager.get_all(cwd)
                print("\n=== Project Facts ===")
                if facts:
                    for k, v in facts.items():
                        print(f"  {k}: {v}")
                else:
                    print("  (No facts set yet)")
                print("=====================\n")
            elif len(parts) >= 4 and parts[1].lower() == "set":
                k, v = parts[2], parts[3]
                facts_manager.set(cwd, k, v)
                print(f"[*] Set fact: {k} = {v}")
            elif len(parts) >= 3 and parts[1].lower() == "remove":
                k = parts[2]
                facts_manager.remove(cwd, k)
                print(f"[*] Removed fact: {k}")
            else:
                print("Usage: /facts | /facts set <key> <value> | /facts remove <key>")
                
        elif cmd.lower().startswith("/pin"):
            if cmd.lower() == "/pins":
                pins = pins_manager.get_all(cwd)
                print("\n=== Pinned Memory ===")
                if pins:
                    for p in pins:
                        print(f"  [ID: {p['id']}] {p['content']}")
                else:
                    print("  (No pinned memory yet)")
                print("=====================\n")
            elif cmd.lower().startswith("/pin "):
                text = cmd[5:].strip()
                if text:
                    pid = pins_manager.add(cwd, content=text)
                    print(f"[*] Pinned memory added (ID: {pid})")
            elif cmd.lower() == "/pin":
                if last_ai_response:
                    pid = pins_manager.add(cwd, content=last_ai_response, source="ai")
                    print(f"[*] Last AI response pinned (ID: {pid})")
                else:
                    print("[!] No previous AI response to pin.")
                    
        elif cmd.lower().startswith("/unpin "):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].isdigit():
                pid = int(parts[1])
                if pins_manager.remove(cwd, pid):
                    print(f"[*] Removed pinned memory (ID: {pid})")
                else:
                    print(f"[!] Pinned memory not found (ID: {pid})")
            else:
                print("Usage: /unpin <id>")
                
        elif cmd.lower() == "/clearpins":
            pins_manager.clear(cwd)
            print("[*] All pinned memory cleared.")
            
        elif cmd.lower() == "/history":
            sessions = memory_manager.get_project_sessions(cwd)
            if not sessions:
                print("No past sessions found for this project.")
            else:
                print("\n=== Past Chat Sessions ===")
                for sid, created_at, msg_count, name in sessions:
                    marker = " (Active)" if sid == runtime.session_id else ""
                    disp_name = f" - \"{name}\"" if name else ""
                    print(f"  [{sid}] {created_at} - {msg_count} messages{disp_name}{marker}")
                print("==========================\n")
                
        elif cmd.lower().startswith("/load "):
            parts = cmd.split()
            if len(parts) < 2 or not parts[1].isdigit():
                print("Usage: /load <session_id>")
            else:
                target_id = int(parts[1])
                runtime.session_id = target_id
                print(f"[*] Loaded chat session ID: {runtime.session_id}")
                
        elif cmd.lower() == "/clear":
            runtime.session_id = memory_manager.create_session(cwd)
            print(f"[*] Memory cleared. Started new session (ID: {runtime.session_id})")
            
        elif cmd.lower().startswith("/session"):
            parts = cmd.split()
            if len(parts) == 1 or parts[1] == "list":
                sessions = memory_manager.get_project_sessions(cwd)
                if not sessions:
                    print("No past sessions found for this project.")
                else:
                    print("\n=== Past Chat Sessions ===")
                    for sid, created_at, msg_count, name in sessions:
                        marker = " (Active)" if sid == runtime.session_id else ""
                        disp_name = f" - \"{name}\"" if name else ""
                        print(f"  [{sid}] {created_at} - {msg_count} messages{disp_name}{marker}")
                    print("==========================\n")
            elif parts[1] in ["enter", "load"]:
                if len(parts) < 3 or not parts[2].isdigit():
                    print("Usage: /session enter <id>")
                else:
                    target_id = int(parts[2])
                    runtime.session_id = target_id
                    print(f"[*] Loaded chat session ID: {runtime.session_id}")
            elif parts[1] == "delete":
                if len(parts) < 3 or not parts[2].isdigit():
                    print("Usage: /session delete <id>")
                else:
                    target_id = int(parts[2])
                    if memory_manager.delete_session(target_id):
                        print(f"[*] Deleted session ID: {target_id}")
                        if runtime.session_id == target_id:
                            runtime.session_id = memory_manager.create_session(cwd)
                            print(f"[*] Active session was deleted. Created new session (ID: {runtime.session_id})")
                    else:
                        print(f"[!] Session {target_id} not found.")
            elif parts[1] == "clear-all":
                count = memory_manager.clear_project_sessions(cwd)
                print(f"[*] Cleared {count} sessions for this project.")
                runtime.session_id = memory_manager.create_session(cwd)
                print(f"[*] Started new session (ID: {runtime.session_id})")
            else:
                print("Usage: /session [list | enter <id> | delete <id> | clear-all]")
                
        elif cmd.startswith("/"):
            print(f"[!] Unknown command: {cmd}")
            
        else:
            # Regular Chat
            from nexa.core.utils.spinner import Spinner
            import re
            import os
            
            # Auto-Context Injection: Detect @file or @directory: mentions
            context_texts = []
            words = cmd.split()
            
            from nexa.core.ai.knowledge.dependency import DependencyParser
            from nexa.core.ai.knowledge.resolver import ModuleResolver
            from nexa.core.ai.knowledge.summarizer import RegexSummarizer
            
            dep_parser = DependencyParser()
            resolver = ModuleResolver(os.getcwd())
            summarizer = RegexSummarizer()
            
            for word in words:
                if word.startswith('@search:'):
                    query = word[8:].replace('_', ' ')
                    import subprocess
                    print(f"[*] Native Search: Scanning project for `{query}`...")
                    try:
                        result = subprocess.run(
                            ['findstr', '/S', '/I', '/N', '/C:' + query, os.path.join(cwd, '*.*')],
                            capture_output=True, text=True, timeout=15
                        )
                        if result.stdout:
                            lines = result.stdout.split('\n')
                            if len(lines) > 50:
                                search_res = "\n".join(lines[:50]) + "\n... (TRUNCATED)"
                            else:
                                search_res = result.stdout
                            context_texts.append(f"--- NATIVE SEARCH RESULTS FOR '{query}' ---\n{search_res}\n--- END SEARCH RESULTS ---")
                        else:
                            context_texts.append(f"--- NATIVE SEARCH RESULTS FOR '{query}' ---\nNo matches found in project.\n--- END SEARCH RESULTS ---")
                    except Exception as e:
                        print(f"[!] Native Search Error: {e}")
                    continue
                    
                if word.startswith('@'):
                    # Strip prefixes if any
                    clean_path = word
                    if clean_path.startswith('@directory:'):
                        clean_path = clean_path[11:]
                    elif clean_path.startswith('@file:'):
                        clean_path = clean_path[6:]
                    elif clean_path.startswith('@code:'):
                        clean_path = clean_path[6:]
                    else:
                        clean_path = clean_path[1:]
                        
                    # Remove trailing punctuation
                    clean_path = re.sub(r'[,.!?]$', '', clean_path)
                    
                    if not os.path.exists(clean_path):
                        # Phase 2.8.1: Fuzzy Path Finder (Auto-Correction)
                        found = False
                        for root, dirs, files in os.walk('.'):
                            # Skip hidden directories to speed up search
                            dirs[:] = [d for d in dirs if not d.startswith('.')]
                            for name in files:
                                full_path = os.path.join(root, name)
                                norm_full = full_path.replace('\\', '/')
                                norm_clean = clean_path.replace('\\', '/')
                                if norm_full.endswith(norm_clean):
                                    clean_path = full_path
                                    found = True
                                    print(f"[*] Fuzzy Finder: Auto-corrected path to `{clean_path}`")
                                    break
                            if found:
                                break
                    
                    if os.path.exists(clean_path):
                        if os.path.isfile(clean_path):
                            try:
                                with open(clean_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                context_texts.append(f"--- START OF FILE: {clean_path} ---\n{content}\n--- END OF FILE ---")
                                
                                # Phase 2.8: Auto-resolve dependencies (Max 3 files to save tokens)
                                if clean_path.endswith('.py'):
                                    deps = dep_parser.parse(content, "python", clean_path)
                                    resolved_count = 0
                                    for target, rel_type in deps:
                                        if resolved_count >= 3:
                                            break
                                        resolved_path = resolver.resolve_python_import(target, clean_path)
                                        if resolved_path and resolved_path != clean_path and os.path.exists(resolved_path):
                                            # Interactive Permission Prompt
                                            print(f"[*] Auto-Resolver found dependency: {resolved_path}")
                                            ans = input("    Do you want to include this file in the context? [y/N]: ").strip().lower()
                                            if ans in ['y', 'yes']:
                                                try:
                                                    with open(resolved_path, 'r', encoding='utf-8') as rf:
                                                        r_content = rf.read()
                                                        # Apply Caveman Summarizer to compress dependency
                                                        r_compressed = summarizer.summarize(r_content, "python", resolved_path)
                                                    context_texts.append(f"--- AUTO-RESOLVED DEPENDENCY: {resolved_path} ---\n{r_compressed}\n--- END OF DEPENDENCY ---")
                                                    resolved_count += 1
                                                except Exception:
                                                    pass
                                            else:
                                                print("    Skipped.")
                            except Exception:
                                pass
                        elif os.path.isdir(clean_path):
                            try:
                                items = os.listdir(clean_path)
                                content = "\n".join(items)
                                context_texts.append(f"--- START OF DIRECTORY: {clean_path} ---\n{content}\n--- END OF DIRECTORY ---")
                            except Exception:
                                pass
                                
            final_prompt = cmd
            if context_texts:
                context_joined = "\n\n".join(context_texts)
                final_prompt = f"The user mentions the following files/directories for context:\n{context_joined}\n\nUser Message:\n{cmd}"
            
            # FAST-PATH: Jika user mengetik "terapkan", "eksekusi", "jalankan", "apply", "bisa langsung di terapkan", dll.
            clean_cmd = cmd.strip().lower()
            apply_keywords = [
                "terapkan", "eksekusi", "jalankan", "apply", "execute", "gas", "lanjutkan", 
                "generate", "buatkan", "implementasikan", "bisa langsung di terapkan",
                "boleh langsung di generate", "langsung terapkan", "terapkan sekarang",
                "terapkan plan", "terapkan planning", "terapkan rencananya", "terapkan blueprint",
                "terapkan planning anda tadi", "terapkan planning tadi", "terapkan arsitektur tadi"
            ]
            is_apply_cmd = (
                any(kw in clean_cmd for kw in ["terapkan", "eksekusi", "jalankan", "apply", "execute", "generate sekarang", "langsung di generate", "langsung generate", "langsung terapkan", "buat sekarang", "gas sekarang", "lanjutkan generate", "di terapkan", "diterapkan"])
                or any(clean_cmd == kw for kw in apply_keywords)
                or clean_cmd.startswith("terapkan")
                or clean_cmd.startswith("eksekusi")
                or clean_cmd.startswith("jalankan")
            )
            last_cached_plan = getattr(runtime, "last_plan", None)
            
            if is_apply_cmd:
                # Auto-switch to BUILD mode
                Config.set("agent.mode", "BUILD")
                
                # If in-memory plan is None (e.g. after /exit restart), load from persistent SQLite or local .nexa/plan.json
                if not last_cached_plan:
                    # 1. Try SQLite session_plans table
                    cached_dict = memory_manager.load_session_plan(runtime.session_id)
                    
                    # 2. Try local workspace .nexa/plan.json file
                    if not cached_dict:
                        local_plan_file = os.path.join(cwd, ".nexa", "plan.json")
                        if os.path.exists(local_plan_file):
                            try:
                                import json
                                with open(local_plan_file, "r", encoding="utf-8") as pf:
                                    cached_dict = json.load(pf)
                            except Exception:
                                pass

                    if cached_dict:
                        from nexa.core.ai.planner.schema import PlanningResult, WorkItem, ConfidenceAssessment
                        work_items_raw = cached_dict.get("work_items", [])
                        work_items = [
                            WorkItem(
                                title=w.get("title", f"Step {i+1}"),
                                description=w.get("description", ""),
                                affected_files=w.get("affected_files", []),
                                objective=w.get("objective", "")
                            ) if isinstance(w, dict) else w
                            for i, w in enumerate(work_items_raw)
                        ]
                        last_cached_plan = PlanningResult(
                            goal=cached_dict.get("goal", "Execute Cached Architecture Plan"),
                            summary=cached_dict.get("summary", ""),
                            objective=cached_dict.get("objective", ""),
                            constraints=cached_dict.get("constraints", []),
                            work_items=work_items,
                            acceptance_criteria=[],
                            risk_analysis=[],
                            clarifications=[],
                            confidence=ConfidenceAssessment(level="HIGH", score=100, reason="Loaded from persistent session disk cache", missing_information="")
                        )
                        runtime.last_plan = last_cached_plan
                    else:
                        # 3. Fallback: Reconstruct from past session messages
                        past_msgs = memory_manager.load_session_messages(runtime.session_id, limit=8)
                        assistant_plans = [m for m in reversed(past_msgs) if m.get("role") == "assistant" and len(m.get("content", "")) > 100]
                        if assistant_plans:
                            latest_content = assistant_plans[0]["content"]
                            from nexa.core.ai.planner.schema import PlanningResult, WorkItem, ConfidenceAssessment
                            work_items = [
                                WorkItem(
                                    title="1. Generate Architecture & Configuration Schema",
                                    description="Create or update nexa.yaml with defined models and relationship fields",
                                    affected_files=["nexa.yaml"],
                                    objective="Define schema models and configurations"
                                ),
                                WorkItem(
                                    title="2. Execute Scaffolding & Database Migration",
                                    description="Generate MVC boilerplate, controllers, models, routes, and execute migrations",
                                    affected_files=["app/", "database/", "routes/"],
                                    objective="Scaffold project structure and database tables"
                                )
                            ]
                            last_cached_plan = PlanningResult(
                                goal="Implement Previous Architectural Blueprint",
                                summary=latest_content,
                                objective="Scaffold project and execute database migrations",
                                constraints=[],
                                work_items=work_items,
                                acceptance_criteria=[],
                                risk_analysis=[],
                                clarifications=[],
                                confidence=ConfidenceAssessment(level="HIGH", score=100, reason="Recovered from session history", missing_information="")
                            )
                            runtime.last_plan = last_cached_plan

                if last_cached_plan:
                    from nexa.core.events.bus import EventContext
                    from nexa.core.models.enums import EventPriority
                    import datetime
                    
                    print("\n[🚀 BUILD MODE - Menjalankan Rencana Arsitektur Sebelumnya...]\n")
                    runtime.bus.publish(EventContext(
                        event_name="BeforeApproval",
                        timestamp=datetime.datetime.now().isoformat(),
                        source="AIPlannerEngine",
                        priority=EventPriority.HIGH,
                        session_id=runtime.session_id,
                        payload={
                            "files": getattr(last_cached_plan, "affected_files", []) if not isinstance(last_cached_plan, dict) else last_cached_plan.get("affected_files", []),
                            "plan": last_cached_plan
                        }
                    ))
                    return True
                else:
                    print("\n[!] Belum ada Cetak Biru (Plan) aktif yang tersimpan. Silakan susun rancangan terlebih dahulu di PLAN mode, atau ketik deskripsi sistem yang ingin dibuat.\n")
                    return True

            # --- PHASE 2.13: Intent Classifier (Smart Router) ---
            try:
                router_provider = ProviderFactory.create()
                intent_sys = (
                    "You are an Intent Classifier for an AI assistant. "
                    "Classify the user's input into one of these EXACT categories:\n"
                    "- 'PLAN COMMIT' (If user wants to create a commit or git push)\n"
                    "- 'PLAN REFACTOR' (If user wants to refactor or restructure code)\n"
                    "- 'PLAN BUGFIX' (If user wants to fix an error or bug)\n"
                    "- 'PLAN' (If user wants code creation/modification, OR asks a question about the codebase like 'where is X' or 'how does Y work' that requires searching)\n"
                    "- 'CHAT' (ONLY if user is just chatting casually, saying hi, or asking general concepts unrelated to the local codebase)\n"
                    "Output ONLY the category name."
                )
                with Spinner("Classifying Intent..."):
                    raw_intent = router_provider.generate([
                        {"role": "system", "content": intent_sys},
                        {"role": "user", "content": cmd}
                    ])
                    intent_str = (raw_intent.get("content", "") if isinstance(raw_intent, dict) else str(raw_intent)).strip().upper()
            except Exception as e:
                if "429" in str(e):
                    print("\n[!] \033[91m🚨 API Limit Terlampaui (429 Too Many Requests).\033[0m")
                    print("[!] Harap istirahat sekitar 1 menit sebelum bertanya lagi, atau pindah ke model lokal: \033[93m/select-provider ollama\033[0m\n")
                    return True
                intent_str = "CHAT"
                
            if "PLAN" in intent_str:
                from nexa.core.ai.context.registry import ContextProviderRegistry
                registry = ContextProviderRegistry()
                auto_context = registry.resolve(intent_str, cwd)
                
                # Gabungkan context teks manual (dari @file) dengan auto_context
                final_context = ""
                if context_texts:
                    final_context += "\n\n".join(context_texts) + "\n\n"
                if auto_context:
                    final_context += auto_context
                from nexa.core.ai.agent_loop import AILoopEngine
                from nexa.core.ai.planner.schema import PlannerContext
                
                # --- Clarification Gate (tahap 0.5) ---
                # Tanya user jika goal terlalu ambigu sebelum pipeline LLM dimulai (hanya pada pesan pembuka tanpa konteks sebelumnya)
                from nexa.core.ai.cognitive.engines.clarification import ClarificationEngine
                clarification_engine = ClarificationEngine()
                past_messages_ctx = memory_manager.load_session_messages(runtime.session_id, limit=4)
                eval_result = clarification_engine.evaluate(cmd, past_messages=past_messages_ctx)
                
                enriched_goal = cmd
                if eval_result.needs_clarification:
                    if hasattr(runtime, 'tui_mode') and runtime.tui_mode:
                        import threading
                        from nexa.core.events.bus import EventContext
                        from nexa.core.models.enums import EventPriority
                        import datetime
                        
                        answer_event = threading.Event()
                        user_answers = {}
                        
                        def on_clarification_answered(ctx):
                            nonlocal user_answers
                            if ctx.event_name == "ClarificationAnswered":
                                user_answers = ctx.payload.get("answers", {})
                                answer_event.set()
                                
                        runtime.bus.subscribe("ClarificationAnswered", on_clarification_answered)
                        
                        runtime.bus.publish_async(EventContext(
                            event_name="ClarificationRequested",
                            timestamp=datetime.datetime.now().isoformat(),
                            source="ClarificationEngine",
                            priority=EventPriority.HIGH,
                            session_id=runtime.session_id,
                            payload={"questions": [q.__dict__ for q in eval_result.questions]}
                        ))
                        
                        answer_event.wait()
                        runtime.bus.unsubscribe("ClarificationAnswered", on_clarification_answered)
                        
                        if user_answers:
                            enrichment_parts = [f"{k}: {v}" for k, v in user_answers.items() if v]
                            if enrichment_parts:
                                enriched_goal = (
                                    f"{cmd}\n"
                                    f"[User Clarification]\n"
                                    + "\n".join(f"- {p}" for p in enrichment_parts)
                                )
                    else:
                        enriched_goal = clarification_engine.ask_user(cmd)
                
                planner_context = PlannerContext(
                    project_path=cwd,
                    knowledge_context=final_context,
                    project_facts=facts_manager.get_all(cwd),
                    pinned_memory=pins_manager.get_all(cwd),
                    conversation_memory=memory_manager.load_session_messages(runtime.session_id, limit=6),
                    user_goal=enriched_goal
                )
                
                # PHASE 1: Using AILoopEngine instead of AIPlannerEngine
                planner = AILoopEngine(bus=runtime.bus)
                with Spinner("Agent Loop Execution..."):
                    report = planner.run_loop(planner_context, session_id=runtime.session_id)
                    
                if report and report.success:
                    work_items = getattr(report.plan, "work_items", []) if not isinstance(report.plan, dict) else report.plan.get("work_items", [])
                    stages = getattr(report.plan, "stages", []) if not isinstance(report.plan, dict) else report.plan.get("stages", [])
                    clarifications = getattr(report.plan, "clarifications", []) if not isinstance(report.plan, dict) else report.plan.get("clarifications", [])
                    
                    if clarifications:
                        print(f"\n╔══ Nexa membutuhkan klarifikasi ══╗")
                        print(f"║ Saya tidak menemukan bukti yang cukup untuk membuat rencana eksekusi.")
                        print(f"╚═══════════════════════════════════╝\n")
                        for idx, q in enumerate(clarifications, 1):
                            print(f"[{idx}] {q}")
                        print("\nSilakan berikan informasi di atas untuk melanjutkan.")
                        memory_manager.save_message(runtime.session_id, "user", final_prompt)
                        memory_manager.save_message(runtime.session_id, "assistant", "Meminta klarifikasi tambahan: " + " | ".join(clarifications))
                        
                    agent_mode = Config.get("agent.mode", "PLAN").upper()
                    from nexa.core.ai.planner.formatter import PlanFormatter
                    runtime.last_plan = report.plan
                    memory_manager.save_session_plan(runtime.session_id, report.plan)
                    try:
                        nexa_local_dir = os.path.join(cwd, ".nexa")
                        os.makedirs(nexa_local_dir, exist_ok=True)
                        import dataclasses, json
                        p_dict = dataclasses.asdict(report.plan) if dataclasses.is_dataclass(report.plan) else report.plan
                        with open(os.path.join(nexa_local_dir, "plan.json"), "w", encoding="utf-8") as pf:
                            json.dump(p_dict, pf, indent=2)
                    except Exception:
                        pass
                    
                    full_plan_markdown = PlanFormatter().to_markdown(report.plan)
                    
                    if agent_mode == "PLAN":
                        # In PLAN mode: Render full architectural plan, strategy, and work items without triggering write approval
                        memory_manager.save_message(runtime.session_id, "user", final_prompt)
                        plan_display = full_plan_markdown if full_plan_markdown and full_plan_markdown.strip() else getattr(report.plan, "summary", "")
                        print(f"\n[🔍 PLAN MODE - Architecture Blueprint & Execution Strategy]\n{plan_display}\n\n💡 (Note: Code changes are locked in PLAN mode. Press TAB or type '/mode build' to execute this plan.)\n")
                        memory_manager.save_message(runtime.session_id, "assistant", plan_display)
                    elif not work_items and not stages:
                        # LLM hanya melakukan investigasi (Search & Answer)
                        memory_manager.save_message(runtime.session_id, "user", final_prompt)
                        summary_text = getattr(report.plan, "summary", "") if not isinstance(report.plan, dict) else report.plan.get("summary", "")
                        memory_manager.save_message(runtime.session_id, "assistant", summary_text)
                    else:
                        # TRIGGER APPROVAL WORKFLOW (BUILD MODE)
                        # Print the plan directly to chat so the user immediately sees the blueprint before the approval modal
                        print(f"\n[🚀 BUILD MODE - Ready to Execute Blueprint]\n{full_plan_markdown}\n\n👉 Silakan setujui eksekusi pada dialog persetujuan (tekan Enter / Y untuk lanjut, N untuk batal)...\n")
                        
                        from nexa.core.events.bus import EventContext
                        from nexa.core.models.enums import EventPriority
                        import datetime
                        runtime.bus.publish(EventContext(
                            event_name="BeforeApproval",
                            timestamp=datetime.datetime.now().isoformat(),
                            source="AIPlannerEngine",
                            priority=EventPriority.HIGH,
                            session_id=runtime.session_id,
                            payload={
                                "files": getattr(report.plan, "affected_files", []) if not isinstance(report.plan, dict) else report.plan.get("affected_files", []),
                                "plan": report.plan
                            }
                        ))
                        
                        memory_manager.save_message(runtime.session_id, "user", final_prompt)
                        memory_manager.save_message(runtime.session_id, "assistant", full_plan_markdown)
                else:
                    err_msg = report.error_message if report else "Terjadi kesalahan internal saat merancang plan."
                    if "429" in err_msg:
                        print("\n[!] \033[91m🚨 Provider API Limit Terlampaui (429 Too Many Requests) saat melakukan Search/Plan.\033[0m")
                        print("[!] Harap tunggu sekitar 1 menit, ATAU gunakan jalan pintas \033[93m@search:<kata_kunci>\033[0m untuk menghemat kuota limit.\n")
                    else:
                        print(f"\n[!] Planning Failed: {err_msg}\n")
                return True
            # --- END OF INTENT CLASSIFIER ---

            if context_texts:
                context_joined = "\n\n".join(context_texts)
                final_prompt = f"The user mentions the following files/directories for context:\n{context_joined}\n\nUser Message:\n{cmd}"
            
            # Save user message to memory
            memory_manager.save_message(runtime.session_id, "user", final_prompt)
            
            # Load rolling window memory
            past_messages = memory_manager.load_session_messages(runtime.session_id, limit=6)
            
            # Phase 2.11: Inject Facts and Pins
            facts = facts_manager.get_all(cwd)
            pins = pins_manager.get_all(cwd)
            
            enhanced_sys_prompt = system_base_prompt
            agents_txt = load_agents_instructions(cwd)
            if agents_txt:
                enhanced_sys_prompt += f"\n\nProject AGENTS.md Instructions:\n{agents_txt}"
            
            # Autonomous Skills Auto-Injection
            from nexa.core.ai.skills import SkillManager
            skill_mgr = SkillManager(cwd)
            skills_prompt = skill_mgr.format_skills_for_prompt()
            if skills_prompt:
                enhanced_sys_prompt += f"\n\n{skills_prompt}"

            if facts:
                facts_str = "\n".join([f"- {k}: {v}" for k, v in facts.items()])
                enhanced_sys_prompt += f"\n\nProject Facts:\n{facts_str}"
            if pins:
                pins_str = "\n".join([f"- {p['content']}" for p in pins])
                enhanced_sys_prompt += f"\n\nPinned User Preferences:\n{pins_str}"
                
            enhanced_sys_prompt += "\n\nUse the provided file contexts to answer the user's questions."
            
            messages = [
                {"role": "system", "content": enhanced_sys_prompt}
            ]
            messages.extend(past_messages)

            try:
                from nexa.core.agent.loop import AgentLoop
                provider = ProviderFactory.create()
                
                spinner_msg = f"Thinking ({provider.__class__.__name__})..."
                if context_texts:
                    file_count = len(context_texts)
                    main_files = [w for w in words if w.startswith('@')]
                    if main_files:
                        main_name = os.path.basename(re.sub(r'[,.!?]$', '', main_files[0].replace('@', '')))
                        spinner_msg = f"Analyzing `{main_name}` + {file_count - 1} dependencies via {provider.__class__.__name__}..." if file_count > 1 else f"Analyzing `{main_name}` via {provider.__class__.__name__}..."
                    else:
                        spinner_msg = f"Analyzing {file_count} contexts via {provider.__class__.__name__}..."
                        
                with Spinner(spinner_msg):
                    loop = AgentLoop(runtime=runtime, system_prompt=enhanced_sys_prompt, provider=provider)
                    content = loop.run(final_prompt, conversation_history=past_messages)
                
                # Save AI response to memory
                memory_manager.save_message(runtime.session_id, "assistant", content)
                last_ai_response = content
                
                # Print AI response in Cyan color
                CYAN = '\033[96m'
                RESET = '\033[0m'
                print(f"\n{CYAN}{content}{RESET}\n")
                
            except Exception as e:
                if "429" in str(e):
                    print("\n[!] \033[91m🚨 Provider API Limit Terlampaui (429 Too Many Requests).\033[0m")
                    print("[!] Harap tunggu sekitar 1 menit, atau pindah ke model lokal: \033[93m/select-provider ollama\033[0m\n")
                else:
                    print(f"[!] Chat Error: {e}\n")

        return True

    import sys
    if sys.stdout.isatty():
        try:
            from nexa.ui.app import NexaApp
            from nexa.core.agent.session import SessionRecoveryManager
            from nexa.core.ai.providers.factory import ProviderFactory
            from nexa.core.observability.usage_tracking import UsageTrackingProvider
            
            # Session preamble before TUI starts
            recovery = SessionRecoveryManager(runtime.memory)
            recovered_id = recovery.prompt_recovery(runtime.cwd)
            if recovered_id is not None:
                runtime.session_id = recovered_id
            else:
                runtime.session_id = runtime.memory.create_session(runtime.cwd)
                
            runtime.enable_tui_mode()

            # --- WRAP provider agar mem-publish TokenUsage (HANYA untuk TUI) ---
            _original_create = ProviderFactory.create.__func__  # classmethod unwrap

            def _tracked_create(cls):
                inner = _original_create(cls)      # panggil implementasi asli
                return UsageTrackingProvider(inner, runtime.bus, lambda: runtime.session_id)

            ProviderFactory.create = classmethod(_tracked_create)

            app = NexaApp(command_handler, runtime)
            try:
                app.run()
            finally:
                ProviderFactory.create = classmethod(_original_create)  # restore
                runtime.bus.shutdown(wait=True)
            return
        except Exception as e:
            print(f"[!] Failed to start Textual UI: {e}. Falling back to basic shell.")

    runtime.start_loop(get_input, command_handler)
