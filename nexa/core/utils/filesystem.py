import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_template(template_path):

    path = BASE_DIR / 'templates' / template_path

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def render_template(content, context):
    # 1. Handle simple loops: [loop:key]...[/loop]
    import re
    loop_pattern = re.compile(r'\[loop:(\w+)\](.*?)\[/loop\]', re.DOTALL)
    
    def replace_loop(match):
        key = match.group(1)
        template_chunk = match.group(2)
        items = context.get(key, [])
        if not isinstance(items, list):
            return ""
        
        rendered_chunks = []
        for item in items:
            chunk = template_chunk
            # If item is a dict or has attributes, we could do more. 
            # For now, let's assume item has a .name or is a string
            if hasattr(item, 'name'):
                chunk = chunk.replace('{{ item.name }}', getattr(item, 'name'))
            if hasattr(item, 'type'):
                chunk = chunk.replace('{{ item.type }}', getattr(item, 'type'))
            if isinstance(item, str):
                chunk = chunk.replace('{{ item }}', item)
            rendered_chunks.append(chunk)
        return "".join(rendered_chunks)

    content = loop_pattern.sub(replace_loop, content)

    # 2. Handle simple variables: {{ key }}
    for key, value in context.items():
        if not isinstance(value, list):
            content = content.replace(f'{{{{ {key} }}}}', str(value))

    return content


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)