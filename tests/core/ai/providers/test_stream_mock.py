import unittest
from nexa.core.ai.providers.mock import MockProvider

class TestStreamMock(unittest.TestCase):
    def test_stream_matches_generate(self):
        provider = MockProvider()
        messages = [{"role": "user", "content": "analyze"}]
        
        # Test generate
        gen_result = provider.generate(messages)
        full_content = gen_result.get("content", "")
        
        # Test stream
        stream_chunks = list(provider.stream(messages))
        stream_content = "".join(stream_chunks)
        
        # They should be identical
        self.assertEqual(stream_content, full_content)
        
        # Check chunk sizes (should be max 5 as per implementation, except maybe the last one)
        for chunk in stream_chunks:
            self.assertLessEqual(len(chunk), 5)

if __name__ == "__main__":
    unittest.main()
