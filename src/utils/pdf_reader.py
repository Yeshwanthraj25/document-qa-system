import io
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from src.utils.exceptions.custom_exceptions import InvalidDocumentError
from src.utils.exceptions.error_codes import ErrorCode


def read_pdf(file_bytes: bytes) -> list[tuple[int, str]]:
    pages =  []
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted :
            raise InvalidDocumentError(ErrorCode.PDF_UNREADABLE)
        for page_number,page in enumerate(reader.pages,1):
            text = page.extract_text() or ""
            if not  text.strip():
                continue
            pages.append(page_number,text)
    except PdfReadError as exc:
        raise  InvalidDocumentError(ErrorCode.DOCUMENT_UNREADABLE) from exc
    if not pages:
        raise InvalidDocumentError(ErrorCode.DOCUMENT_NO_TEXT)
    return pages
   
def read_text(file_bytes: bytes) -> list[tuple[int, str]]:
    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InvalidDocumentError(ErrorCode.DOCUMENT_UNREADABLE) from exc
    text = text.replace("\r\n","\n")
    if not text.strip(): 
        raise InvalidDocumentError(ErrorCode.DOCUMENT_NO_TEXT)
    return [(1,text)]


                




   