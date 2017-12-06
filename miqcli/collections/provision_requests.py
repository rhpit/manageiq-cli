import click


class Collections(object):
    """Provision requests collections."""

    def approve(self):
        """Approve."""
        raise NotImplementedError

    def create(self):
        """Create."""
        raise NotImplementedError

    def deny(self):
        """Deny."""
        raise NotImplementedError

    def query(self):
        """Query."""
        raise NotImplementedError
