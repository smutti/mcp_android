import unittest

from errors import UiElementNotFoundError, ValidationError
from ui.selector_service import SelectorService


class FakeObject:
    def __init__(self, found):
        self.found = found
        self.clicked = False

    def wait(self, timeout):
        return self.found

    def click(self):
        self.clicked = True


class FakeDevice:
    def __init__(self, found=True):
        self.obj = FakeObject(found)

    def __call__(self, **kwargs):
        return self.obj


class SelectorServiceTest(unittest.TestCase):
    def test_selector_requires_exactly_one_selector(self):
        with self.assertRaises(ValidationError):
            SelectorService.click(FakeDevice(), text="a", resource_id="id")

    def test_selector_not_found(self):
        with self.assertRaises(UiElementNotFoundError):
            SelectorService.click(FakeDevice(found=False), text="missing")

    def test_selector_click_success(self):
        device = FakeDevice(found=True)
        result = SelectorService.click(device, text="hello")
        self.assertIn("Clicked element", result)
        self.assertTrue(device.obj.clicked)


if __name__ == "__main__":
    unittest.main()
