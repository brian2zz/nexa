import os

class CodeExtractor:
    @staticmethod
    def parse_and_extract(target: str) -> dict:
        """
        Parses a target string like 'path/to/file.py:10-25' or 'path/to/file.py:10'
        Returns a dict: {'file_path': str, 'start_line': int, 'end_line': int, 'code': str, 'error': str}
        """
        result = {
            'file_path': '',
            'start_line': 0,
            'end_line': 0,
            'code': '',
            'error': None
        }
        
        parts = target.split(':')
        if len(parts) < 2:
            result['error'] = "Invalid format. Expected 'file_path:start_line-end_line' or 'file_path:line'."
            return result
            
        file_path = parts[0]
        lines_part = parts[1]
        
        result['file_path'] = file_path
        
        try:
            if '-' in lines_part:
                s, e = lines_part.split('-')
                result['start_line'] = int(s)
                result['end_line'] = int(e)
            else:
                result['start_line'] = int(lines_part)
                result['end_line'] = int(lines_part)
        except ValueError:
            result['error'] = "Invalid line numbers. Must be integers."
            return result
            
        if not os.path.exists(file_path):
            result['error'] = f"File not found: {file_path}"
            return result
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            start_idx = max(0, result['start_line'] - 1)
            end_idx = min(len(lines), result['end_line'])
            
            extracted_lines = lines[start_idx:end_idx]
            result['code'] = "".join(extracted_lines)
            
        except Exception as e:
            result['error'] = f"Error reading file: {str(e)}"
            
        return result
