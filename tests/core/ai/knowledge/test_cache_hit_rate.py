import os
import tempfile
import unittest
from nexa.core.ai.knowledge.cache.sqlite import SQLiteCache
from nexa.core.ai.knowledge.summarizer import RegexSummarizer

class TestSemanticCacheHitRate(unittest.TestCase):
    def test_cache_hit_rate(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            db_path = os.path.join(temp_dir, "test_cache.db")
            
            # Setup cache and summarizer
            cache = SQLiteCache(db_path=db_path)
            summarizer = RegexSummarizer(cache=cache)
            
            # Monkey patch cache.set to track cache misses
            set_call_count = 0
            original_set = cache.set
            
            def mock_set(key, val):
                nonlocal set_call_count
                set_call_count += 1
                return original_set(key, val)
                
            cache.set = mock_set
            
            code_snippet = "def hello():\n    print('world')\n"
            
            # First call (should miss cache and call set)
            res1 = summarizer.summarize(code_snippet, "python", "hello.py")
            self.assertEqual(set_call_count, 1)
            
            # Second call (should hit cache, no new set calls)
            res2 = summarizer.summarize(code_snippet, "python", "hello.py")
            self.assertEqual(set_call_count, 1, "Cache hit failed! Set was called again.")
            
            # Assert results are identical
            self.assertEqual(res1.functions, res2.functions)
            
            # Close first cache to release file lock on Windows
            if hasattr(cache, 'conn') and cache.conn:
                cache.conn.close()
            
            # Instantiate a completely new cache and summarizer (to simulate new run)
            cache2 = SQLiteCache(db_path=db_path)
            summarizer2 = RegexSummarizer(cache=cache2)
            
            # Monkey patch again
            set_call_count2 = 0
            original_set2 = cache2.set
            
            def mock_set2(key, val):
                nonlocal set_call_count2
                set_call_count2 += 1
                return original_set2(key, val)
                
            cache2.set = mock_set2
            
            # Third call on a new instance (should hit persistent cache)
            res3 = summarizer2.summarize(code_snippet, "python", "hello.py")
            self.assertEqual(set_call_count2, 0, "Persistent cache hit failed! Set was called on new instance.")
            self.assertEqual(res1.functions, res3.functions)
            
            if hasattr(cache2, 'conn') and cache2.conn:
                cache2.conn.close()

if __name__ == '__main__':
    unittest.main()
