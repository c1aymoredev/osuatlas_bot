class Language:
    def unknown_command(self, command):
        return f"Unknown command: {command}"

    def external_exception(self, details):
        return f"An external error occurred: {details}"

    def internal_exception(self, details):
        return f"An internal error occurred: {details}"