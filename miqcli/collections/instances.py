class Collections(object):
    """Instances collections."""

    def query(self):
        """Query."""
        raise NotImplementedError

    def terminate(self):
        """Terminate."""
        raise NotImplementedError

    def stop(self):
        """Stop."""
        raise NotImplementedError

    def start(self):
        """Start."""
        raise NotImplementedError

    def pause(self):
        """Pause."""
        raise NotImplementedError

    def suspend(self):
        """Suspend."""
        raise NotImplementedError

    def shelve(self):
        """Shelve."""
        raise NotImplementedError

    def reboot_guest(self):
        """Reboot guest."""
        raise NotImplementedError

    def reset(self):
        """Reset."""
        raise NotImplementedError
