import uiautomator2 as u2


class U2ClientProvider:
    """Creates uiautomator2 device connections."""

    @staticmethod
    def connect(serial: str):
        return u2.connect(serial)
