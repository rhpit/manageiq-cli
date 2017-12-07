class Collections(object):
    """Service requests collections."""

    def query(self):
        """Query."""
        raise NotImplementedError

    def approve(self):
        """Approve."""
        raise NotImplementedError

    def deny(self):
        """Deny."""
        raise NotImplementedError

    def delete(self):
        """Delete."""
        raise NotImplementedError

    def add_approver(self):
        """Add approver."""
        raise NotImplementedError

    def remove_approver(self):
        """Remove approver."""
        raise NotImplementedError

    def edit(self):
        """Edit."""
        raise NotImplementedError
