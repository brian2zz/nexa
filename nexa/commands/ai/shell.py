import sys
import getpass
from nexa.config import Config
from nexa.core.ai.providers.factory import ProviderFactory

def print_help():
    print("\nNexa AI Interactive Shell - Commands:")
    print("  /select-provider <name>  : Switch AI Provider (ollama, deepseek, mock)")
    print("  /set-model <name>        : Set the active model for the current provider")
    print("  /set-api-key             : Securely enter API Key for current provider")
    print("  /status                  : Show current configuration")
    print("  /history                 : Show chat session history")
    print("  /load <id>               : Load a past chat session")
    print("  /clear                   : Clear current chat session")
    print("  /plan <goal>             : Generate an Execution Plan for a task")
    print("  /facts                   : Show project facts")
    print("  /facts set <k> <v>       : Set a project fact")
    print("  /facts remove <k>        : Remove a project fact")
    print("  /pin [text]              : Pin last AI response or text")
    print("  /pins                    : Show pinned memory")
    print("  /unpin <id>              : Remove a pinned memory")
    print("  /clearpins               : Clear all pinned memory")
    print("  /commands                : Show available CLI commands for this project")
    print("  /exit, /quit, exit       : Exit the shell")
    print("  /help                    : Show this help message\n")

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
        from nexa.commands.ai.completer import NexaMentionCompleter
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
        
        current_session_id = memory_manager.create_session(cwd)
        last_ai_response = ""
        print(f"[*] Started new chat session (ID: {current_session_id})")
        
        provider_completer = WordCompleter(['ollama', 'deepseek', 'groq', 'mock'], ignore_case=True)
        path_completer = PathCompleter(only_directories=False, expanduser=True)
        
        slash_completer = NestedCompleter.from_nested_dict({
            '/help': None,
            '/status': None,
            '/select-provider': provider_completer,
            '/set-model': None,
            '/set-api-key': None,
            '/dir': path_completer,
            '/explain': path_completer,
            '/history': None,
            '/load': None,
            '/clear': None,
            '/plan': None,
            '/facts': None,
            '/pin': None,
            '/pins': None,
            '/unpin': None,
            '/clearpins': None,
            '/commands': None,
            '/exit': None,
            '/quit': None,
        })
        
        # Combine slash commands with inline @ mentions
        completer = NexaMentionCompleter(slash_completer)
        
        session = PromptSession(history=InMemoryHistory(), completer=completer)
        
        def get_input():
            return session.prompt("Nexa> ").strip()
    except ImportError:
        def get_input():
            return input("Nexa> ").strip()
            
    while True:
        try:
            cmd = get_input()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Nexa AI Shell.")
            break
            
        if not cmd:
            continue
            
        if cmd.lower() in ["/exit", "/quit", "exit", "quit"]:
            print("Exiting Nexa AI Shell.")
            break
            
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
                print("Usage: /select-provider <name> (e.g. ollama, deepseek)")
            else:
                provider_name = parts[1].lower()
                Config.set("provider", provider_name)
                print(f"[*] Provider switched to: {provider_name}")
                check_provider_readiness(provider_name)
                
        elif cmd.lower().startswith("/set-model"):
            parts = cmd.split()
            if len(parts) < 2:
                print("Usage: /set-model <model_name>")
            else:
                model_name = parts[1]
                provider = Config.get("provider")
                Config.set(f"{provider}.model", model_name)
                print(f"[*] Model for {provider} set to: {model_name}")
                
        elif cmd.lower() == "/set-api-key":
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
                continue
                
            target = parts[1]
            extracted = CodeExtractor.parse_and_extract(target)
            
            if extracted.get('error'):
                print(f"[!] {extracted['error']}")
                continue
                
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
                continue
                
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
                continue
                
            from nexa.core.ai.planner import AIPlannerEngine, PlannerContext
            
            # Gather context
            facts = facts_manager.get_all(cwd)
            pins = pins_manager.get_all(cwd)
            past_messages = memory_manager.load_session_messages(current_session_id, limit=6)
            
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
                report = planner.plan(planner_context)
                
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
                for sid, created_at, msg_count in sessions:
                    marker = " (Active)" if sid == current_session_id else ""
                    print(f"  [{sid}] {created_at} - {msg_count} messages{marker}")
                print("==========================\n")
                
        elif cmd.lower().startswith("/load "):
            parts = cmd.split()
            if len(parts) < 2 or not parts[1].isdigit():
                print("Usage: /load <session_id>")
            else:
                target_id = int(parts[1])
                current_session_id = target_id
                print(f"[*] Loaded chat session ID: {current_session_id}")
                
        elif cmd.lower() == "/clear":
            current_session_id = memory_manager.create_session(cwd)
            print(f"[*] Memory cleared. Started new session (ID: {current_session_id})")
            
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
            
            # --- PHASE 2.13: Intent Classifier (Smart Router) ---
            try:
                router_provider = ProviderFactory.create()
                intent_sys = (
                    "You are an Intent Classifier for an AI assistant. "
                    "If the user asks to CREATE, BUILD, REFACTOR, MODIFY, or DELETE code/files, output ONLY the word 'PLAN'. "
                    "If the user is just asking a question, asking for an explanation, or chatting, output ONLY the word 'CHAT'."
                )
                with Spinner("Classifying Intent..."):
                    raw_intent = router_provider.generate([
                        {"role": "system", "content": intent_sys},
                        {"role": "user", "content": cmd}
                    ])
                    intent_str = (raw_intent.get("content", "") if isinstance(raw_intent, dict) else str(raw_intent)).strip().upper()
            except Exception:
                intent_str = "CHAT"
                
            if "PLAN" in intent_str:
                from nexa.core.ai.planner import AIPlannerEngine, PlannerContext
                planner_context = PlannerContext(
                    project_path=cwd,
                    knowledge_context="\n\n".join(context_texts) if context_texts else "",
                    project_facts=facts_manager.get_all(cwd),
                    pinned_memory=pins_manager.get_all(cwd),
                    conversation_memory=memory_manager.load_session_messages(current_session_id, limit=6),
                    user_goal=cmd
                )
                planner = AIPlannerEngine()
                with Spinner("Planning Execution..."):
                    report = planner.plan(planner_context)
                if report.success:
                    GREEN = '\033[92m'
                    RESET = '\033[0m'
                    print(f"\n{GREEN}{report.to_markdown()}{RESET}\n")
                    memory_manager.save_message(current_session_id, "user", final_prompt)
                    memory_manager.save_message(current_session_id, "assistant", "[Execution Plan Generated]")
                else:
                    print(f"\n[!] Planning Failed: {report.error_message}\n")
                continue
            # --- END OF INTENT CLASSIFIER ---

            if context_texts:
                context_joined = "\n\n".join(context_texts)
                final_prompt = f"The user mentions the following files/directories for context:\n{context_joined}\n\nUser Message:\n{cmd}"
            
            # Save user message to memory
            memory_manager.save_message(current_session_id, "user", final_prompt)
            
            # Load rolling window memory
            past_messages = memory_manager.load_session_messages(current_session_id, limit=6)
            
            # Phase 2.11: Inject Facts and Pins
            facts = facts_manager.get_all(cwd)
            pins = pins_manager.get_all(cwd)
            
            enhanced_sys_prompt = system_base_prompt
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
                provider = ProviderFactory.create()
                
                spinner_msg = f"Thinking ({provider.__class__.__name__})..."
                if context_texts:
                    file_count = len(context_texts)
                    # Try to get the main file name from the prompt
                    main_files = [w for w in words if w.startswith('@')]
                    if main_files:
                        main_name = os.path.basename(re.sub(r'[,.!?]$', '', main_files[0].replace('@', '')))
                        spinner_msg = f"Analyzing `{main_name}` + {file_count - 1} dependencies via {provider.__class__.__name__}..." if file_count > 1 else f"Analyzing `{main_name}` via {provider.__class__.__name__}..."
                    else:
                        spinner_msg = f"Analyzing {file_count} contexts via {provider.__class__.__name__}..."
                        
                with Spinner(spinner_msg):
                    raw_resp = provider.generate(messages)
                    content = raw_resp.get("content", "") if isinstance(raw_resp, dict) else str(raw_resp)
                
                # Save AI response to memory
                memory_manager.save_message(current_session_id, "assistant", content)
                last_ai_response = content
                
                # Print AI response in Cyan color
                CYAN = '\033[96m'
                RESET = '\033[0m'
                print(f"\n{CYAN}{content}{RESET}\n")
                
            except Exception as e:
                print(f"[!] Chat Error: {e}\n")
