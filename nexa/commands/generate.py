import os
import time
import shutil
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

        snapshot = None
        if not flags["dry_run"]:
            snapshot = self.take_snapshot()

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
            if snapshot is not None:
                self.rollback_snapshot(snapshot)
        except Exception as e:
            self.logger.error(f"FATAL ERROR: {str(e)}")
            if snapshot is not None:
                self.rollback_snapshot(snapshot)

    def take_snapshot(self):
        snapshot = set()
        root_dir = os.getcwd()
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if any(p in dirpath for p in ['node_modules', '.git', '__pycache__']):
                continue
            snapshot.add(dirpath)
            for f in filenames:
                snapshot.add(os.path.join(dirpath, f))
        return snapshot

    def rollback_snapshot(self, snapshot):
        root_dir = os.getcwd()
        self.logger.warning("Rolling back newly created files and directories due to failure...")
        
        dirs_to_remove = []
        files_to_remove = []
        
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if any(p in dirpath for p in ['node_modules', '.git', '__pycache__']):
                continue
            
            if dirpath not in snapshot:
                parent = os.path.dirname(dirpath)
                if parent in snapshot:
                    dirs_to_remove.append(dirpath)
                dirnames.clear()
                continue
                
            for f in filenames:
                path = os.path.join(dirpath, f)
                if path not in snapshot:
                    files_to_remove.append(path)
                    
        for f in files_to_remove:
            try:
                os.remove(f)
            except:
                pass
                
        for d in dirs_to_remove:
            try:
                shutil.rmtree(d)
            except:
                pass
                
        self.logger.success("Rollback complete. Workspace restored to previous state.")

    def render_errors(self, errors):
        """
        Structured error rendering for CLI with high visibility.
        """
        self.logger.error("!!! SCHEMA VALIDATION FAILED !!!")
        print("\n" + "!" * 60)
        for error in errors:
            print(f"  [ERROR] [{error.code.upper()}] {error.message}")
            if error.model:
                print(f"          > Location: App({error.app}) -> Model({error.model}) -> Field({error.field or 'Any'})")
        print("!" * 60 + "\n")
        self.logger.warning("Please fix the issues in your schema and re-run generation.")

def handle(args):
    cmd = GenerateCommand(args)
    cmd.run()
