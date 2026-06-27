import os
import argparse
from nexa.core.ai.memory import Memory
from nexa.core.ai.knowledge.models import ScannerResult, AnalyzerResult as StaticResult
from nexa.core.ai.providers.factory import ProviderFactory
from nexa.config import Config
from nexa.core.utils.spinner import Spinner

def handle(args):
    parser = argparse.ArgumentParser(description="Analyze project")
    parser.add_argument("--format", type=str, default="text", choices=["text", "json", "markdown", "html"])
    parser.add_argument("--goal", type=str, default="Perform general project analysis and identify tech debt")
    parser.add_argument("--provider", type=str, help="Provider to use (e.g. ollama, deepseek)")
    parsed_args, _ = parser.parse_known_args(args)
    
    if parsed_args.provider:
        Config.set("provider", parsed_args.provider)
        
    root_path = os.path.abspath(os.getcwd())
    memory = Memory()
    project = memory.get_project(root_path)
    
    if not project:
        print("[!] Project belum dipindai. Silakan jalankan 'nexa scan' terlebih dahulu.")
        return
        
    files = memory.get_files(project['id'])
    
    # Adapt to new Schema
    scanner_result = ScannerResult(
        project_root=root_path,
        files=files
    )
    static_result = StaticResult(
        framework=project.get('framework', 'Unknown'),
        language=project.get('language', 'Unknown')
    )
    
    # Set default to ollama if not specified, then create via factory
    if not Config.get("provider"):
        Config.set("provider", "ollama")
        
    try:
        provider = ProviderFactory.create()
    except Exception as e:
        print(f"[!] {e}")
        return
        
    from nexa.core.ai.analyzer import AIAnalyzer, OutputFormatter
    analyzer = AIAnalyzer(provider=provider)
    formatter = OutputFormatter()
    
    print(f"[*] Analyzing with Goal: '{parsed_args.goal}'")
    with Spinner(f"Running AI Analyzer (Provider: {provider.__class__.__name__})..."):
        result = analyzer.analyze(
            goal=parsed_args.goal,
            scanner_result=scanner_result,
            static_result=static_result
        )
    
    if result.success:
        output = formatter.format(result.report, parsed_args.format)
        print(output)
        if result.warnings:
            for w in result.warnings:
                print(f"[!] {w}")
    else:
        print("[!] Analysis Failed!")
        for e in result.errors:
            print(f"- {e}")
        print(f"Raw Response:\n{result.raw_response}")
