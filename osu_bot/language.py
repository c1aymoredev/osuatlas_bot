class Language:
    def unknown_command(self, command):
        return f"Неизвестная команда: {command}"

    def external_exception(self, details):
        return f"Произошла внешняя ошибка: {details}"

    def internal_exception(self, details):
        return f"Произошла внутренняя ошибка: {details}"