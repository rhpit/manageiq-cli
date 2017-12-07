class Collections(object):
    """Automation requests collections."""

    def create(self):
        """Create."""
        raise NotImplementedError

    def approve(self):
        """Approve."""
        raise NotImplementedError

    def deny(self):
        """Deny."""
        raise NotImplementedError
