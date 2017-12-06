class Collections(object):
    """Automate domains collections."""

    def query(self):
        """Query."""
        raise NotImplementedError

    def refresh_from_source(self):
        """Refresh from source."""
        raise NotImplementedError
