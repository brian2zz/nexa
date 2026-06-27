import argparse
import sys
from nexa.core.utils.extractor import CodeExtractor
from nexa.core.utils.spinner import Spinner
from nexa.core.ai.providers.factory import ProviderFactory
from nexa.config import Config

def handle(args):
    parser = argparse.ArgumentParser(description="Explain a specific code snippet")
    parser.add_argument("target", help="Format: path/to/file.py:start_line-end_line")
    parser.add_argument("--provider", type=str, help="Provider to use (e.g. ollama, deepseek)")
    parsed_args, _ = parser.parse_known_args(args)
    
    if parsed_args.provider:
        Config.set("provider", parsed_args.provider)
        
    extracted = CodeExtractor.parse_and_extract(parsed_args.target)
    
    if extracted.get('error'):
        print(f"[!] {extracted['error']}")
        return
        
    code = extracted['code']
    file_path = extracted['file_path']
    start = extracted['start_line']
    end = extracted['end_line']
    
    prompt = (
        f"Please explain the following code from file `{file_path}` "
        f"(lines {start} to {end}):\n\n"
        f"```\n{code}\n```\n\n"
        f"Keep the explanation concise and easy to understand."
    )
    
    messages = [
        {"role": "system", "content": "You are Nexa AI, an expert coding assistant."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        provider = ProviderFactory.create()
    except Exception as e:
        print(f"[!] Provider Error: {e}")
        return
        
    print(f"[*] Explaining `{file_path}` (lines {start}-{end}) ...")
    
    with Spinner(f"Thinking ({provider.__class__.__name__})..."):
        try:
            raw_resp = provider.generate(messages)
            content = raw_resp.get("content", "") if isinstance(raw_resp, dict) else str(raw_resp)
        except Exception as e:
            content = f"Error communicating with provider: {str(e)}"
            
    print("\n" + "="*50)
    print(content)
    print("="*50 + "\n")
