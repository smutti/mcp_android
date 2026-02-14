from errors import UiElementNotFoundError, ValidationError


class SelectorService:
    """Finds UI elements by selector and performs high-level actions."""

    @staticmethod
    def click(
        u2_device,
        text: str | None = None,
        resource_id: str | None = None,
        content_desc: str | None = None,
        timeout_s: float = 10.0,
    ) -> str:
        selectors = [bool(text), bool(resource_id), bool(content_desc)]
        if sum(selectors) != 1:
            raise ValidationError("Exactly one selector must be provided: text, resource_id, content_desc")

        if text:
            obj = u2_device(text=text)
            selector_label = f"text={text}"
        elif resource_id:
            obj = u2_device(resourceId=resource_id)
            selector_label = f"resource_id={resource_id}"
        else:
            obj = u2_device(description=content_desc)
            selector_label = f"content_desc={content_desc}"

        found = False
        if hasattr(obj, "wait"):
            found = bool(obj.wait(timeout=timeout_s))
        elif hasattr(obj, "exists"):
            exists = obj.exists
            found = bool(exists() if callable(exists) else exists)

        if not found:
            raise UiElementNotFoundError(f"UI element not found for selector {selector_label}")

        obj.click()
        return f"Clicked element with selector {selector_label}"
