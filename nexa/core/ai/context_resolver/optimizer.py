import re

class ContextOptimizer:
    """
    Optimizes the context by removing excessive whitespaces and comments.
    """
    def optimize(self, code: str) -> str:
        if not code:
            return ""
            
        # Remove excessive blank lines
        code = re.sub(r'\n\s*\n', '\n\n', code)
        
        # In a real implementation we would strip comments based on language,
        # but for V1 we do a basic stripping of lines that only contain comments
        lines = code.split('\n')
        optimized_lines = []
        for line in lines:
            stripped = line.strip()
            # Basic comment stripping (Python/PHP/JS single line)
            if stripped.startswith('//') or stripped.startswith('#') and not stripped.startswith('#['):
                continue
            optimized_lines.append(line)
            
        return "\n".join(optimized_lines)
