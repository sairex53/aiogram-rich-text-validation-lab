from __future__ import annotations

import json
import unittest

from pydantic import ValidationError

from rich_text_lab import build_envelope, nested_value


class TaggedRichTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = build_envelope(discriminated=True)

    def test_deep_nested_text_is_parsed_into_concrete_models(self) -> None:
        parsed = self.model.model_validate({"value": nested_value(100)})
        node = parsed.value
        kinds = ("spoiler", "subscript", "bold", "italic", "underline")
        for index in range(100):
            self.assertEqual(node.type, kinds[index % len(kinds)])
            node = node.text
        self.assertEqual(node, "sample")

    def test_json_and_plain_string_branches(self) -> None:
        raw = json.dumps({"value": ["plain", {"type": "bold", "text": "strong"}]})
        parsed = self.model.model_validate_json(raw)
        self.assertEqual(parsed.value[0], "plain")
        self.assertEqual(parsed.value[1].type, "bold")

    def test_model_instances_are_accepted(self) -> None:
        first = self.model.model_validate({"value": {"type": "bold", "text": "strong"}})
        second = self.model.model_validate({"value": first.value})
        self.assertEqual(second.value.type, "bold")

    def test_unknown_type_has_a_single_tag_error(self) -> None:
        with self.assertRaises(ValidationError) as caught:
            self.model.model_validate({"value": {"type": "unknown", "text": "x"}})
        self.assertEqual(caught.exception.errors()[0]["type"], "union_tag_invalid")


if __name__ == "__main__":
    unittest.main()
