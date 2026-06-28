import os

with open('nexa/commands/ai/shell.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if 'except Exception as e:' in lines[i] and i > 590:
        lines[i] = '            except Exception as e:\n'
    if 'print(f"[!] Chat Error: {e}\\n")' in lines[i] and i > 590:
        lines[i] = '                print(f"[!] Chat Error: {e}\\n")\n'
    if 'return True' in lines[i] and i > 590:
        lines[i] = '        return True\n'
    if 'runtime.start_loop(get_input, command_handler)' in lines[i]:
        lines[i] = '    runtime.start_loop(get_input, command_handler)\n'

with open('nexa/commands/ai/shell.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
