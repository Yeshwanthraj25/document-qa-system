from src.utils.exceptions.error_codes import ErrorCode


class AppError(Exception):
    def __init__(self, error_code: ErrorCode, detail: str | None = None):
        self.error_code = error_code
        self.detail = detail
        super().__init__(detail or error_code.message)
    
class InvalidDocumentError(AppError):
    pass