"""
Доменные исключения приложения.
"""


class AppError(Exception):
    """
    Базовое исключение приложения.
    Все доменные ошибки наследуются от этого класса.
    """

    def __init__(self, message: str = "Application error occurred"):
        self.message = message
        super().__init__(self.message)


class ConflictError(AppError):
    """
    Ошибка конфликта данных.
    """

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message)


class UnauthorizedError(AppError):
    """
    Ошибка аутентификации.
    """

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class ForbiddenError(AppError):
    """
    Ошибка авторизации (прав доступа).
    """

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message)


class NotFoundError(AppError):
    """
    Ошибка "не найдено".
    """

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class ExternalServiceError(AppError):
    """
    Ошибка внешнего сервиса.
    """

    def __init__(
        self, message: str = "External service error", service_name: str = "Unknown"
    ):
        self.service_name = service_name
        super().__init__(f"{service_name}: {message}")
