import sys
import subprocess
import importlib
import os
from nexa import __version__
from nexa.commands.registry import GROUPS, render_root_help, render_group_help, render_command_help

def detect_project_type() -> str:
    """Mendeteksi tipe project secara cerdas menggunakan ProjectDetector."""
    try:
        from nexa.core.ai.scanner.detector import ProjectDetector
        detector = ProjectDetector()
        info = detector.detect('.')
        fw = info.get('framework', '').lower()
        lang = info.get('language', '').lower()
        
        if 'django' in fw or 'fastapi' in fw:
            return 'django'
        if 'flutter' in fw or lang == 'dart':
            return 'flutter'
        if 'php' in lang or 'laravel' in fw or 'nexaphp' in fw or 'codeigniter' in fw:
            return 'php'
    except Exception:
        pass

    # Fallback heuristik cepat
    if os.path.exists('manage.py'):
        return 'django'
    if os.path.exists('pubspec.yaml'):
        return 'flutter'
    if os.path.exists('artisan') or os.path.exists('composer.json') or os.path.exists('bin/nexa'):
        return 'php'
    return 'unknown'

def dispatch(args):
    if not args:
        render_root_help()
        return

    command = args[0]
    
    if command in ['-v', '--version', 'version']:
        print(f"\033[96mNexa AI Framework v{__version__}\033[0m")
        return
        
    if command in ['help', '-h', '--help']:
        if len(args) > 1:
            if args[1] in GROUPS:
                render_group_help(args[1])
            else:
                print(f"Untuk bantuan spesifik grup, jalankan: nexa {args[1]} help")
        else:
            render_root_help()
        return

    if command == 'update':
        print("[INFO] Mengunduh dan memperbarui Nexa Framework dari GitHub...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', '--no-cache-dir', 'git+https://github.com/brian2zz/nexa.git'
        ])
        print("✅ Nexa berhasil diperbarui ke versi terbaru!")
        return

    # Check if command is a group
    if command in GROUPS:
        sub_args = args[1:]
        if not sub_args:
            render_group_help(command)
            return
            
        subcommand = sub_args[0]
        if subcommand in ['help', '-h', '--help']:
            render_group_help(command)
            return
            
        # Check if subcommand is asking for help
        if len(sub_args) > 1 and sub_args[1] in ['help', '-h', '--help']:
            render_command_help(command, subcommand)
            return
            
        # Find subcommand in group
        target_module = None
        for cmd in GROUPS[command]:
            if cmd["name"] == subcommand:
                target_module = cmd["module"]
                break
                
        if target_module:
            try:
                module = importlib.import_module(target_module)
                module.handle(sub_args[1:])
            except Exception as e:
                print(f"[!] Gagal mengeksekusi {command} {subcommand}: {e}")
                import traceback
                traceback.print_exc()
        else:
            # Fallbacks for specific groups
            if command == 'django':
                subprocess.run(['python', 'manage.py', subcommand, *sub_args[1:]])
            elif command == 'flutter':
                subprocess.run(['flutter', subcommand, *sub_args[1:]], shell=(os.name == 'nt'))
            elif command == 'php':
                if os.path.exists('artisan'):
                    subprocess.run(['php', 'artisan', subcommand, *sub_args[1:]])
                elif os.path.exists('package.json'):
                    subprocess.run(['npm', 'run', subcommand, *sub_args[1:]], shell=(os.name == 'nt'))
                else:
                    print(f"Unknown PHP subcommand: {subcommand}")
            else:
                print(f"[!] Unknown subcommand '{subcommand}' for group '{command}'")
        return

    # Top-level shorthand resolving
    shorthands = {}
    for group, cmds in GROUPS.items():
        if group == 'ai': continue # Do not auto-detect AI commands at top level anymore (breaking change)
        for cmd in cmds:
            name = cmd["name"]
            if name not in shorthands:
                shorthands[name] = []
            shorthands[name].append((group, cmd["module"]))
            
    if command in shorthands:
        options = shorthands[command]
        detected_type = detect_project_type()
        
        # If auto-detect works and matches one of the options
        matched_option = next((opt for opt in options if opt[0] == detected_type), None)
        if matched_option:
            print(f"[AUTO-DETECT] Project {detected_type.capitalize()} terdeteksi. Mengarahkan ke 'nexa {detected_type} {command}'...")
            module = importlib.import_module(matched_option[1])
            module.handle(args[1:])
            return
            
        # If project type is detected but command is native fallback
        if detected_type != 'unknown':
            print(f"[AUTO-DETECT] Project {detected_type.capitalize()} terdeteksi. Menjalankan '{command}' sebagai perintah native...")
            if detected_type == 'django':
                subprocess.run(['python', 'manage.py', command, *args[1:]])
            elif detected_type == 'flutter':
                subprocess.run(['flutter', command, *args[1:]], shell=(os.name == 'nt'))
            elif detected_type == 'php':
                if os.path.exists('artisan'):
                    subprocess.run(['php', 'artisan', command, *args[1:]])
                elif os.path.exists('package.json'):
                    subprocess.run(['npm', 'run', command, *args[1:]], shell=(os.name == 'nt'))
            return
            
        # If unknown and only one choice
        if len(options) == 1:
            platform = options[0][0]
            print(f"[HINT] Mengarahkan ke 'nexa {platform} {command}'...")
            module = importlib.import_module(options[0][1])
            module.handle(args[1:])
            return
            
        # If unknown and multiple choices
        print(f"🤔 Perintah '{command}' tersedia di beberapa platform, dan tipe project tidak dapat dideteksi otomatis.")
        for i, opt in enumerate(options, 1):
            print(f"{i}) {opt[0].capitalize()}")
        try:
            choice = input(f"Pilih platform target (1-{len(options)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                opt = options[int(choice)-1]
                module = importlib.import_module(opt[1])
                module.handle(args[1:])
            else:
                print("❌ Pilihan tidak valid. Dibatalkan.")
        except KeyboardInterrupt:
            print("\n❌ Dibatalkan.")
        return

    # Native command fallback based on detected type
    detected_type = detect_project_type()
    if detected_type == 'django':
        subprocess.run(['python', 'manage.py', command, *args[1:]])
    elif detected_type == 'flutter':
        subprocess.run(['flutter', command, *args[1:]], shell=(os.name == 'nt'))
    elif detected_type == 'php' and os.path.exists('artisan'):
        subprocess.run(['php', 'artisan', command, *args[1:]])
    else:
        print(f"❌ Perintah '{command}' tidak dikenali dan bukan dalam project Django/Flutter/PHP yang valid.")

def main():
    if sys.stdout.encoding != 'utf-8' and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    args = sys.argv[1:]
    dispatch(args)

if __name__ == '__main__':
    main()