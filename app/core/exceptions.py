"""generic Application Exceptions."""

from loguru import logger


class ApplicationCaseError(Exception):
    """Base exception - user-friendly message untuk UI."""

    def __init__(self, message: str, service_name: str | None = None):
        self.message = message
        self.service_name = service_name
        logger.warning(f"ApplicationCaseError: {message} | Service: {service_name}")
        super().__init__(self.message)

    def __str__(self):
        return self.message


class BackEndServiceError(ApplicationCaseError):
    """Exception untuk backend service errors."""

    def __init__(self, service_name: str | None = None, error: Exception | None = None):
        error_detail = str(error) if error else "Unknown error"
        message = f"Backend error [{service_name}]: {error_detail}"
        logger.error(f"BackEndServiceError [{service_name}]", exc_info=error)
        super().__init__(message=message, service_name=service_name)
