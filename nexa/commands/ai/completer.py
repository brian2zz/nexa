from prompt_toolkit.completion import Completer, Completion, WordCompleter, PathCompleter
from prompt_toolkit.document import Document

class NexaMentionCompleter(Completer):
    def __init__(self, slash_completer):
        self.slash_completer = slash_completer
        self.dir_completer = PathCompleter(only_directories=True, expanduser=True)
        self.file_completer = PathCompleter(only_directories=False, expanduser=True)
        
        # We also provide completions for the explicit prefixes
        self.prefix_completer = WordCompleter(['@directory:', '@file:', '@code:'], ignore_case=True)

    def get_completions(self, document: Document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)

        if document.text.lstrip().startswith('/'):
            # Delegate to slash commands completer (like /explain, /dir, /set-model)
            yield from self.slash_completer.get_completions(document, complete_event)
            return

        if word_before_cursor.startswith('@'):
            # If they just typed "@" or a partial prefix, suggest @directory:, @file:, etc.
            if len(word_before_cursor) <= 1 or word_before_cursor in ('@directory', '@file', '@code', '@d', '@f', '@c'):
                yield from self.prefix_completer.get_completions(document, complete_event)
            
            if word_before_cursor.startswith('@directory:'):
                # Autocomplete for directories only
                path_word = word_before_cursor[11:]
                sub_doc = Document(path_word, cursor_position=len(path_word))
                for c in self.dir_completer.get_completions(sub_doc, complete_event):
                    yield Completion(c.text, start_position=c.start_position, display=c.display)
            
            elif word_before_cursor.startswith('@file:'):
                # Autocomplete for files & directories
                path_word = word_before_cursor[6:]
                sub_doc = Document(path_word, cursor_position=len(path_word))
                for c in self.file_completer.get_completions(sub_doc, complete_event):
                    yield Completion(c.text, start_position=c.start_position, display=c.display)
                    
            elif word_before_cursor.startswith('@code:'):
                # No specific autocompletion for code snippets yet, but we allow it
                pass
                
            else:
                # Raw @path mention (treat as @file:)
                path_word = word_before_cursor[1:]
                # We skip standard prefix suggestions if they actually typed a real path prefix
                if not any(word_before_cursor.startswith(p) for p in ['@directory', '@file', '@code']):
                    sub_doc = Document(path_word, cursor_position=len(path_word))
                    for c in self.file_completer.get_completions(sub_doc, complete_event):
                        yield Completion(c.text, start_position=c.start_position, display=c.display)

class DynamicModelCompleter(Completer):
    def get_completions(self, document: Document, complete_event):
        from nexa.config import Config
        provider = Config.get("provider", "ollama").lower()
        models = []
        
        if provider == "ollama":
            models = ['qwen2.5-coder', 'qwen2.5', 'llama3.1', 'mistral', 'gemma2']
        elif provider == "deepseek":
            models = ['deepseek-chat', 'deepseek-coder']
        elif provider == "groq":
            models = ['llama-3.1-8b-instant', 'llama-3.1-70b-versatile']
        elif provider == "gemini":
            models = ['gemini-2.5-flash', 'gemini-1.5-pro', 'gemini-1.5-flash']
        elif provider == "mock":
            models = ['mock-model']
            
        word_before_cursor = document.get_word_before_cursor(WORD=True).lower()
        for m in models:
            if m.lower().startswith(word_before_cursor):
                yield Completion(m, start_position=-len(word_before_cursor))

