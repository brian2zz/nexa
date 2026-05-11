from nexa.core.schema.loaders.yaml_loader import YamlLoader
from nexa.core.pipeline.project_pipeline import ProjectPipeline
from nexa.core.validators.schema_validator import SchemaValidationError

def test_pipeline():
    # 1. Load Schema
    loader = YamlLoader()
    try:
        project = loader.load('nexa.yaml')
    except Exception as e:
        print(f"Failed to load YAML: {e}")
        return

    # 2. Run Pipeline
    pipeline = ProjectPipeline()
    
    try:
        pipeline.run(project)
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
