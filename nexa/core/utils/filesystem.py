import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_template(template_path):

    path = BASE_DIR / 'templates' / template_path

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def render_template(content, context):
    import re

    # Helper to resolve complex expressions like "item.name" or "model_name.lower()"
    def resolve_val(expr, ctx):
        parts = expr.split('.')
        val = ctx.get(parts[0])
        
        for part in parts[1:]:
            if val is None: break
            
            # Handle methods like .lower()
            if part.endswith('()'):
                method_name = part[:-2]
                if hasattr(val, method_name):
                    val = getattr(val, method_name)()
            # Handle attributes
            elif hasattr(val, part):
                val = getattr(val, part)
            elif isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return f"MISSING:{expr}"
        return str(val) if val is not None else ""

    # 1. Handle Loops: [loop:key]...[/loop]
    loop_pattern = re.compile(r'\[loop:(\w+)\](.*?)\[/loop\]', re.DOTALL)
    
    def replace_loop(match):
        key = match.group(1)
        template_chunk = match.group(2)
        items = context.get(key, [])
        if not isinstance(items, list): return ""
        
        rendered_chunks = []
        for item in items:
            # Render chunk with item in local context
            chunk = template_chunk
            # Find all {{ item.xxx }} in chunk (whitespace tolerant)
            item_vars = re.findall(r'{{\s*item\.(.*?)\s*}}', chunk)
            for var_path in item_vars:
                # Resolve the value from the current item
                val = resolve_val(var_path.strip(), {"item": item})
                # Replace the exact tag including potential whitespace
                # Use a specific regex for each replacement to be safe
                tag_regex = re.compile(rf'{{\s*item\.{re.escape(var_path)}\s*}}')
                chunk = tag_regex.sub(val, chunk)
            
            # Simple {{ item }} replacement
            if isinstance(item, str):
                chunk = chunk.replace('{{ item }}', item)
                
            rendered_chunks.append(chunk)
        return "".join(rendered_chunks)

    content = loop_pattern.sub(replace_loop, content)

    # 2. Handle Variables: {{ key.attr }} or {{ key.method() }}
    var_pattern = re.compile(r'{{ (.*?) }}')
    def replace_var(match):
        expr = match.group(1).strip()
        if expr.startswith('item.'): return match.group(0) # Skip loop items, handled above
        
        # Only replace if the root key exists in context
        root_key = expr.split('.')[0]
        if root_key in context:
            return resolve_val(expr, context)
        
        # Otherwise, leave it for Vue/other systems
        return match.group(0)

    return var_pattern.sub(replace_var, content)


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)