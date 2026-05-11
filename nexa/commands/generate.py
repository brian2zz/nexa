import os
import time
from nexa.core.schema.loaders.yaml_loader import YamlLoader
from nexa.core.pipeline.project_pipeline import ProjectPipeline
from nexa.core.validators.schema_validator import SchemaValidationError
from nexa.core.runtime.command import BaseCommand

class GenerateCommand(BaseCommand):
    """
    Command to generate a project from a YAML schema.
    Usage: nexa generate [schema.yaml] [--backend] [--frontend] [--dry-run]
    """
    def run(self):
        # 1. Determine Schema File
        schema_file = 'nexa.yaml'
        for arg in self.args:
            if not arg.startswith('--') and arg.endswith('.yaml'):
                schema_file = arg
                break

        if not os.path.exists(schema_file):
            self.logger.error(f"Schema file '{schema_file}' not found.")
            return

        # 2. Parse Execution Modes
        flags = self.parse_flags()
        # If neither is specified, run both
        if not flags["backend"] and not flags["frontend"]:
            flags["backend"] = True
            flags["frontend"] = True

        self.logger.info(f"Nexa Engine: Initializing generation from '{schema_file}'...")
        if flags["dry_run"]:
            self.logger.warning("DRY RUN MODE: No files will be written.")

        start_time = time.time()

        try:
            # 3. Load & Validate (Pipeline handles this now)
            loader = YamlLoader()
            project = loader.load(schema_file)
            
            pipeline = ProjectPipeline()
            # Pass flags to pipeline
            pipeline.run(project, modes=flags)

            duration = time.time() - start_time
            self.logger.success(f"Project '{project.name}' generated in {duration:.2f}s.")
            self.logger.info("Ready to build! Happy coding with Nexa.")

        except SchemaValidationError as e:
            self.render_errors(e.errors)
        except Exception as e:
            self.logger.error(f"FATAL ERROR: {str(e)}")

    def render_errors(self, errors):
        """
        Structured error rendering for CLI.
        """
        self.logger.error("Schema Validation Failed:")
        print("====================================")
        for error in errors:
            print(f"  - [{error.code.upper()}] {error.message}")
            if error.model:
                print(f"    Location: App({error.app}), Model({error.model}), Field({error.field})")
        print("====================================")

def handle(args):
    cmd = GenerateCommand(args)
    cmd.run()
