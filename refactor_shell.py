import os

def refactor_shell():
    with open('nexa/commands/ai/shell.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    in_loop = False
    loop_indent = ''
    skip_next = 0

    for i, line in enumerate(lines):
        if skip_next > 0:
            skip_next -= 1
            continue
            
        if line.strip() == 'while True:':
            in_loop = True
            loop_indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f'{loop_indent}from nexa.core.agent.runtime import NexaAgentRuntime\n')
            new_lines.append(f'{loop_indent}runtime = NexaAgentRuntime(cwd=cwd)\n\n')
            new_lines.append(f'{loop_indent}def command_handler(cmd):\n')
            # Skip the next 5 lines which are the try/except for get_input()
            #         try:
            #             cmd = get_input()
            #         except (KeyboardInterrupt, EOFError):
            #             print("\nExiting Nexa AI Shell.")
            #             break
            skip_next = 5
            continue
            
        if in_loop:
            if line.strip() == 'except Exception as e:' and 'print(f"[!] Chat Error:' in lines[i+1]:
                # End of the loop block
                new_lines.append(f'{loop_indent}    return True\n\n')
                new_lines.append(f'{loop_indent}runtime.start_loop(get_input, command_handler)\n')
                new_lines.append(line)
                in_loop = False
                continue
                
            # Replace continue with return True
            # Replace break with return False
            l_stripped = line.strip()
            if l_stripped == 'continue':
                line = line.replace('continue', 'return True')
            elif l_stripped == 'break':
                line = line.replace('break', 'return False')
                
            new_lines.append(line)
        else:
            new_lines.append(line)

    with open('nexa/commands/ai/shell_v2.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    refactor_shell()
