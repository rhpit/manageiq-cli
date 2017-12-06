class Collections(object):
    """Virtual machines collections."""

    def query(self):
        """Query."""
        raise NotImplementedError

    def edit(self):
        """Edit."""
        raise NotImplementedError

    def add_lifecycle_event(self):
        """Add lifecycle event."""
        raise NotImplementedError

    def add_event(self):
        """Add event."""
        raise NotImplementedError

    def refresh(self):
        """Refresh."""
        raise NotImplementedError

    def shutdown_guest(self):
        """Shutdown guest."""
        raise NotImplementedError

    def reboot_guest(self):
        """Reboot guest."""
        raise NotImplementedError

    def start(self):
        """Start."""
        raise NotImplementedError

    def stop(self):
        """Stop."""
        raise NotImplementedError

    def suspend(self):
        """Suspend."""
        raise NotImplementedError

    def shelve(self):
        """Shelve."""
        raise NotImplementedError

    def shelve_offload(self):
        """Shelve offload."""
        raise NotImplementedError

    def pause(self):
        """Pause."""
        raise NotImplementedError

    def request_console(self):
        """Request console."""
        raise NotImplementedError

    def reset(self):
        """Reset."""
        raise NotImplementedError

    def retire(self):
        """Retire."""
        raise NotImplementedError

    def set_owner(self):
        """Set owner."""
        raise NotImplementedError

    def set_ownership(self):
        """Set ownership."""
        raise NotImplementedError

    def scan(self):
        """Scan."""
        raise NotImplementedError

    def delete(self):
        """Delete."""
        raise NotImplementedError

    def assign_tags(self):
        """Assign tags."""
        raise NotImplementedError

    def unassign_tags(self):
        """Unassign tags."""
        raise NotImplementedError
