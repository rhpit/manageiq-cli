class Collections(object):
    """Services collections."""

    def query(self):
        """Query."""
        raise NotImplementedError

    def create(self):
        """Create."""
        raise NotImplementedError

    def edit(self):
        """Edit."""
        raise NotImplementedError

    def retire(self):
        """Retire."""
        raise NotImplementedError

    def set_ownership(self):
        """Set ownership."""
        raise NotImplementedError

    def delete(self):
        """Delete."""
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

    def assign_tags(self):
        """Assign tags."""
        raise NotImplementedError

    def unassign_tags(self):
        """Unassign tags."""
        raise NotImplementedError

    def add_resource(self):
        """Add resource."""
        raise NotImplementedError

    def remote_all_resources(self):
        """Remove all resources."""
        raise NotImplementedError

    def remove_resource(self):
        """Remove resource."""
        raise NotImplementedError
