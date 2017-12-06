class Collections(object):
    """Arbitration settings collections."""

    def query(self):
        """Query."""
        raise NotImplementedError

    def create(self):
        """Create."""
        raise NotImplementedError

    def edit(self):
        """Edit."""
        raise NotImplementedError

    def delete(self):
        """Delete."""
        raise NotImplementedError
