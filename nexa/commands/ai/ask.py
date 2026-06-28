import os
import sys
from nexa.core.agent.runtime import NexaAgentRuntime
from nexa.core.ai.providers.factory import ProviderFactory

def handle(args):
    cwd = os.getcwd()
    try:
        runtime = NexaAgentRuntime(cwd=cwd)
    except Exception as e:
        print(f"[!] Gagal memulai Agent Runtime: {e}")
        sys.exit(1)
        
    try:
        from prompt_toolkit import PromptSession
        session = PromptSession()
    except Exception:
        session = None

    def get_input():
        if session:
            try:
                return session.prompt("Nexa[Ask]> ")
            except Exception:
                return input("Nexa[Ask]> ")
        else:
            return input("Nexa[Ask]> ")

    def command_handler(cmd):
        if not cmd:
            return True
            
        if cmd.lower() in ["/exit", "/quit", "exit", "quit"]:
            print("Exiting Nexa Ask Shell.")
            return False

        system_base_prompt = "You are Nexa Ask, a friendly, helpful, and knowledgeable AI assistant. You can answer any questions, including random, general knowledge, or conversational ones. You are not strictly bound to programming."
        
        # --- Context Builder (Bisa baca file jika dimention pakai @) ---
        context_texts = []
        words = cmd.split()
        for w in words:
            if w.startswith('@'):
                path_part = w[1:]
                full_path = os.path.join(cwd, path_part)
                
                if os.path.isdir(full_path):
                    try:
                        files = os.listdir(full_path)
                        context_texts.append(f"Directory `{path_part}` contains:\n" + "\n".join(files))
                    except Exception as e:
                        context_texts.append(f"Could not read directory `{path_part}`: {e}")
                elif os.path.isfile(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        context_texts.append(f"File `{path_part}` content:\n```\n{content}\n```")
                    except Exception as e:
                        context_texts.append(f"Could not read file `{path_part}`: {e}")

        # Gabungkan konteks file jika ada
        if context_texts:
            context_joined = "\n\n".join(context_texts)
            final_cmd = f"Context files provided by user:\n{context_joined}\n\nUser Question:\n{cmd}"
        else:
            final_cmd = cmd
            
        # Simpan pesan user ke memori sesi
        runtime.memory.save_message(runtime.session_id, "user", final_cmd)
        
        # Tarik memori sesi terakhir agar bisa nyambung ngobrolnya
        past_messages = runtime.memory.load_session_messages(runtime.session_id, limit=6)
        
        messages = [{"role": "system", "content": system_base_prompt}]
        for m in past_messages:
            messages.append({"role": m["role"], "content": m["content"]})
            
        # Panggil LLM
        try:
            provider = ProviderFactory.create()
            print("Thinking...", end="\r")
            response = provider.generate(messages)
            
            content = response.get("content", "") if isinstance(response, dict) else str(response)
            
            CYAN = '\033[96m'
            RESET = '\033[0m'
            print(f"\n{CYAN}{content}{RESET}\n")
            
            # Simpan balasan ke memori
            runtime.memory.save_message(runtime.session_id, "assistant", content)
            
        except Exception as e:
            print(f"\n[!] Error generating response: {e}\n")
            
        return True
        
    print("=" * 50)
    print("Welcome to Nexa Ask Shell (General Assistant Mode).")
    print("Tanya apa saja dengan santai! Ketik /exit untuk keluar.")
    print("=" * 50)
    
    runtime.start_loop(get_input, command_handler)
