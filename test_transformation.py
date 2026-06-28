import json
from nexa.core.ai.providers.factory import ProviderFactory
from nexa.core.ai.transformation.engine import TransformationEngine
from nexa.core.ai.transformation.models import TransformationRequest, TransformationMode

def test_nexa_transformation():
    print("=== Testing Nexa AI Transformation Engine ===")
    
    # 1. Init Provider (Ollama/Groq/DeepSeek/Mock)
    print("\n[*] Initializing AI Provider...")
    provider = ProviderFactory.create()
    print(f"    Active Provider: {provider.__class__.__name__}")
    
    # 2. Init Engine
    engine = TransformationEngine(provider)
    
    # 3. Create Request Object (Testing GENERATE mode)
    print("\n[*] Creating TransformationRequest (Mode: GENERATE)...")
    request = TransformationRequest(
        mode=TransformationMode.GENERATE,
        execution_plan={
            "goal": "Buat sebuah fungsi matematika sederhana",
            "steps": ["Buat fungsi pertambahan", "Buat fungsi pengurangan"]
        },
        context_bundle={
            "project_facts": {"language": "python"}
        },
        user_instruction="Tambahkan docstring yang jelas dan berikan contoh penggunaan di bawahnya."
    )
    
    # 4. Process Request (This triggers Prompt Factory, Strategy, and LLM)
    print("\n[*] Running Engine (This may take a few seconds)...")
    result = engine.transform(request)
    
    # 5. Result Object & Metrics
    print("\n=== Transformation Result ===")
    print(f"Success    : {result.success}")
    print(f"Error      : {result.error}")
    print("\n[Generated Code]")
    print(result.generated_code if result.success else "N/A")
    
    print("\n[Explanation / Chat]")
    print(result.explanation if result.success else "N/A")
    
    print("\n[Metrics & Metadata]")
    print(json.dumps(result.metadata, indent=2))
    
    if result.success:
        print("\n✅ Semua komponen (Provider, Factory, Processor, Retry Policy) berjalan dengan baik!")
    else:
        print("\n❌ Terjadi kesalahan pada proses transformasi.")

if __name__ == "__main__":
    test_nexa_transformation()
