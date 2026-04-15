import unittest
import sys
import types

sys.modules.setdefault("requests", types.SimpleNamespace())
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda *args, **kwargs: None))
from backend.ai_service import AIService


class AIServiceResponseParsingTests(unittest.TestCase):
    def setUp(self):
        self.service = AIService()

    def test_extract_response_text_from_string_content(self):
        data = {
            "choices": [
                {
                    "message": {
                        "content": "Summary text"
                    }
                }
            ]
        }

        self.assertEqual(self.service._extract_response_text(data), "Summary text")

    def test_extract_response_text_from_content_blocks(self):
        data = {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "text", "text": "Line one."},
                            {"type": "text", "text": "Line two."}
                        ]
                    }
                }
            ]
        }

        self.assertEqual(
            self.service._extract_response_text(data),
            "Line one.\nLine two."
        )

    def test_extract_response_text_uses_reasoning_fallback(self):
        data = {
            "choices": [
                {
                    "message": {
                        "content": [],
                        "reasoning": "Recovered from reasoning field."
                    }
                }
            ]
        }

        self.assertEqual(
            self.service._extract_response_text(data),
            "Recovered from reasoning field."
        )

    def test_build_empty_response_error_reports_missing_content(self):
        data = {
            "choices": [
                {
                    "message": {}
                }
            ]
        }

        self.assertEqual(
            self.service._build_empty_response_error(data),
            "AI model returned no message content"
        )

    def test_sanitize_extracted_section_discards_placeholders(self):
        self.assertEqual(self.service._sanitize_extracted_section("[summary]"), "")
        self.assertEqual(
            self.service._sanitize_extracted_section("[the full cleaned text]"),
            ""
        )
        self.assertEqual(self.service._sanitize_extracted_section("..."), "")
        self.assertEqual(self.service._sanitize_extracted_section("..., "), "")

    def test_placeholder_meta_text_is_detected(self):
        meta_text = (
            "Wait, but the user said to format exactly as follows: "
            "perhaps just present all parts."
        )

        self.assertTrue(self.service._is_placeholder_text(meta_text))
        self.assertFalse(self.service._is_placeholder_text("Real summary of the document."))

    def test_instruction_echoes_are_detected_as_placeholders(self):
        self.assertTrue(self.service._is_placeholder_text("2-3 sentences."))
        self.assertTrue(self.service._is_placeholder_text("bullet points."))
        self.assertTrue(self.service._is_placeholder_text("tag1, tag2, tag3"))

    def test_extract_error_message_prefers_nested_provider_details(self):
        class FakeResponse:
            status_code = 503
            text = "provider error"

            def json(self):
                return {
                    "error": {
                        "message": "Provider returned error",
                        "metadata": {
                            "provider_name": "OpenRouter",
                            "raw": "openai/gpt-oss-20b:free is temporarily unavailable"
                        }
                    }
                }

        message = self.service._extract_error_message(FakeResponse())
        self.assertIn("Provider returned error", message)
        self.assertIn("openai/gpt-oss-20b:free is temporarily unavailable", message)


if __name__ == "__main__":
    unittest.main()
