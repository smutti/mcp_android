import unittest

from errors import ValidationError
from shared.validators import parse_returned_attributes, validate_log_level


class ValidatorsTest(unittest.TestCase):
    def test_validate_log_level_success(self):
        self.assertEqual(validate_log_level("debug"), "DEBUG")

    def test_validate_log_level_invalid(self):
        with self.assertRaises(ValidationError):
            validate_log_level("TRACE")

    def test_parse_returned_attributes_success(self):
        attributes = parse_returned_attributes("text, resource-id, bounds")
        self.assertEqual(attributes, ["text", "resource-id", "bounds"])

    def test_parse_returned_attributes_invalid(self):
        with self.assertRaises(ValidationError):
            parse_returned_attributes("text,invalid-attr")


if __name__ == "__main__":
    unittest.main()
