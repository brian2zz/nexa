from nexa.core.schema.loaders.yaml_loader import YamlLoader
from nexa.core.validators.schema_validator import SchemaValidator, SchemaValidationError

def test_validation():
    loader = YamlLoader()
    validator = SchemaValidator()
    
    print("Testing valid schema...")
    try:
        project = loader.load('nexa.yaml')
        validator.validate_project_structure(project)
        print("OK: nexa.yaml is valid!")
    except SchemaValidationError as e:
        print(f"ERROR: nexa.yaml failed validation:\n{e}")

    print("\nTesting broken schema...")
    try:
        project = loader.load('broken_nexa.yaml')
        validator.validate_project_structure(project)
        print("OK: broken_nexa.yaml is valid! (Wait, this is wrong)")
    except SchemaValidationError as e:
        print(f"ERROR: broken_nexa.yaml failed validation as expected:\n{e}")

if __name__ == "__main__":
    test_validation()
