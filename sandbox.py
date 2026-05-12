import os
from nexa.core.schema.loaders.yaml_loader import YamlLoader
from nexa.core.pipeline.project_pipeline import ProjectPipeline
from nexa.core.validators.schema_validator import SchemaValidationError

def test_pipeline():
    # Target path
    TARGET_DIR = r"h:\project code\tes_nexa"
    os.chdir(TARGET_DIR)
    
    print(f"[*] Running Sandbox in: {os.getcwd()}")
    
    # 1. Load Schema
    loader = YamlLoader()
    try:
        project = loader.load('nexa.yaml')
    except Exception as e:
        print(f"Failed to load YAML: {e}")
        return

    # 2. Run Pipeline
    pipeline = ProjectPipeline()
    
    # Debug: List registered generators
    from nexa.core.registry import generators
    print("Registered Generators:")
    for entry in generators.list_all():
        print(f"  - {entry.category}.{entry.key} (prio: {entry.priority})")
    print("")
    
    try:
        pipeline.run(project)
        print("\n[SUCCESS] Pipeline executed successfully!")
    except SchemaValidationError as e:
        print("\nPIPELINE FAILED: Validation Errors")
        for error in e.errors:
            print(f"- [{error.code}] {error.message}")
    except Exception as e:
        print(f"\nPIPELINE FAILED: Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline()
