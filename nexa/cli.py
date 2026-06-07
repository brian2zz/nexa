import sys
import subprocess
import importlib
import os

def main():
    args = sys.argv[1:]

    if not args:
        print('Nexa CLI - Framework Developer Tool')
        print('Usage: nexa <command> [args]')
        print('Available Commands:')
        print('  django   - Group of commands related to Django project (e.g. nexa django startapp)')
        print('  flutter  - Group of commands related to Flutter project (e.g. nexa flutter create-module)')
        return

    command = args[0]

    # Mappings untuk built-in nexa django commands
    built_in_commands = {
        'run': 'nexa.commands.django.run',
        'new': 'nexa.commands.django.new',
        'startapp': 'nexa.commands.django.startapp',
        'install': 'nexa.commands.django.install',
        'build': 'nexa.commands.django.build',
        'make:api': 'nexa.commands.django.makeapi',
        'generate': 'nexa.commands.django.generate',
        'doctor': 'nexa.commands.django.doctor',
        'sync': 'nexa.commands.django.sync',
        'inspect': 'nexa.commands.django.inspect',
        'dev': 'nexa.commands.django.dev',
    }

    # Mappings untuk built-in nexa flutter commands
    built_in_flutter_commands = {
        'create-module': 'nexa.commands.flutter.create_module',
        'doctor': 'nexa.commands.flutter.doctor',
        'new': 'nexa.commands.flutter.new',
        'gen-model': 'nexa.commands.flutter.gen_model',
        'run': 'nexa.commands.flutter.run',
        'generate': 'nexa.commands.flutter.generate',
    }

    if command == 'django':
        django_args = args[1:]
        if not django_args:
            print('Nexa Django CLI')
            print('Usage: nexa django <subcommand> [args]')
            print('Available subcommands:')
            for sub in sorted(built_in_commands.keys()):
                print(f'  {sub}')
            return
            
        subcommand = django_args[0]
        sub_args = django_args[1:]
        
        if subcommand in built_in_commands:
            # Memuat modul dinamis
            module_name = built_in_commands[subcommand]
            module = importlib.import_module(module_name)
            module.handle(sub_args)
        else:
            # Fallback otomatis ke python manage.py <subcommand>
            subprocess.run([
                'python',
                'manage.py',
                subcommand,
                *sub_args
            ])

    elif command == 'flutter':
        flutter_args = args[1:]
        if not flutter_args:
            print('Nexa Flutter CLI')
            print('Usage: nexa flutter <subcommand> [args]')
            print('Available subcommands:')
            for sub in sorted(built_in_flutter_commands.keys()):
                print(f'  {sub}')
            return

        subcommand = flutter_args[0]
        sub_args = flutter_args[1:]

        if subcommand in built_in_flutter_commands:
            # Memuat modul dinamis
            module_name = built_in_flutter_commands[subcommand]
            module = importlib.import_module(module_name)
            module.handle(sub_args)
        else:
            # Fallback otomatis ke perintah native flutter (e.g. flutter run, flutter build)
            subprocess.run([
                'flutter',
                subcommand,
                *sub_args
            ], shell=(os.name == 'nt'))
            
    elif command in built_in_commands or command in built_in_flutter_commands:
        options = []
        if command in built_in_commands:
            options.append('django')
        if command in built_in_flutter_commands:
            options.append('flutter')

        if len(options) == 1:
            platform = options[0]
            print(f"[HINT] Mengarahkan ke 'nexa {platform} {command}'...")
            if platform == 'django':
                module_name = built_in_commands[command]
            else:
                module_name = built_in_flutter_commands[command]
            module = importlib.import_module(module_name)
            module.handle(args[1:])
        else:
            print(f"🤔 Perintah '{command}' tersedia di kedua platform.")
            print("1) Django")
            print("2) Flutter")
            try:
                choice = input("Pilih platform target (1/2): ").strip()
                if choice == '1':
                    module_name = built_in_commands[command]
                    module = importlib.import_module(module_name)
                    module.handle(args[1:])
                elif choice == '2':
                    module_name = built_in_flutter_commands[command]
                    module = importlib.import_module(module_name)
                    module.handle(args[1:])
                else:
                    print("❌ Pilihan tidak valid. Dibatalkan.")
            except KeyboardInterrupt:
                print("\n❌ Dibatalkan.")
                return
        
    else:
        # Fallback lama untuk perintah manage.py langsung
        subprocess.run([
            'python',
            'manage.py',
            command,
            *args[1:]
        ])

if __name__ == '__main__':
    main()