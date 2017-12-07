class Collections(object):
    """Requests collections."""

    def query(self):
        """Query."""
        raise NotImplementedError

    def create(self):
        """Create."""
        raise NotImplementedError

    def edit(self):
        """Edit."""
        raise NotImplementedError

    def approve(self):
        """Approve."""
        raise NotImplementedError

    def deny(self):
        """Deny."""
        raise NotImplementedError
