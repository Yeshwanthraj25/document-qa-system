from src.utils.exceptions.custom_exceptions import InvalidDocumentError,AppError
import pytest 
from src.utils.exceptions.error_codes import ErrorCode

def test_app_error_carries_code_and_detail():
    with pytest.raises(AppError) as exc_info:
        raise InvalidDocumentError(ErrorCode.EMPTY_FILE, "no bytes")
    assert exc_info.value.error_code == ErrorCode.EMPTY_FILE
    assert exc_info.value.error_code.http_status == 400
    assert exc_info.value.detail == "no bytes"