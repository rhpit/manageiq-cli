class Collections(object):
    """Notifications collections."""

    def mark_as_seen(self):
        """Mark as seen."""
        raise NotImplementedError

    def delete(self):
        """Delete."""
        raise NotImplementedError
