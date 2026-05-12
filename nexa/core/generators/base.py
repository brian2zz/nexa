import os
from nexa.core.utils.filesystem import load_template, render_template, write_file

class BaseGenerator:
    template_path = ""

    def __init__(self, schema=None):
        self.schema = schema
        # For backward compatibility
        self.model_schema = schema
        self.context = {}

    def build_context(self):
        """
        Build the context dictionary for template rendering.
        To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement build_context")

    def get_target_path(self):
        """
        Calculate the absolute path where the file should be written.
        To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_target_path")

    def render(self):
        """
        Loads the template and renders it with the current context.
        """
        template = load_template(self.template_path)
        return render_template(template, self.context)

    def generate(self):
        """
        The main entry point: builds context, renders, and writes to disk.
        """
        self.build_context()
        target_path = self.get_target_path()
        content = self.render()
        write_file(target_path, content)
        return self.context
