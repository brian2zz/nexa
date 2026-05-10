from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_template(template_path):

    path = BASE_DIR / 'templates' / template_path

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def render_template(content, context):

    for key, value in context.items():

        content = content.replace(
            f'{{{{ {key} }}}}',
            value
        )

    return content


def write_file(path, content):

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)