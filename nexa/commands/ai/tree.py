import os

def handle(args):
    from nexa.core.ai.memory import Memory
    
    root_path = os.path.abspath(os.getcwd())
    memory = Memory()
    project = memory.get_project(root_path)
    
    if not project:
        print("[!] Project belum dipindai. Silakan jalankan 'nexa scan' terlebih dahulu.")
        return
        
    files = memory.get_files(project['id'])
    if not files:
        print("[!] Tidak ada file ditemukan di database.")
        return
        
    print(f"[*] Project Tree for: {os.path.basename(root_path)} ({project['framework']})")
    
    # Build tree
    tree = {}
    for f in files:
        parts = f['path'].split('/')
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
            
    def print_tree(d, indent=""):
        items = list(d.keys())
        for i, key in enumerate(items):
            is_last = (i == len(items) - 1)
            prefix = "\-- " if is_last else "|-- "
            print(indent + prefix + key)
            
            if d[key]:
                next_indent = indent + ("    " if is_last else "|   ")
                print_tree(d[key], next_indent)
                
    print(os.path.basename(root_path))
    print_tree(tree)
