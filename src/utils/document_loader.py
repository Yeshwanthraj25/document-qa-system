from pathlib import Path
from src.utils.pdf_reader import read_text,read_pdf
from src.utils.exceptions.custom_exceptions import InvalidDocumentError
from src.utils.exceptions.error_codes import ErrorCode


LOADERS = {
    ".pdf": read_pdf,
    ".txt": read_text,
    ".md": read_text,
}


def load_document(filename: str | None, file_bytes: bytes) -> list[tuple[int, str]]:

    extension = Path(filename or "").suffix.lower()
    loader = LOADERS.get(extension)
    if loader is None:
        raise InvalidDocumentError(
               ErrorCode.INVALID_FILE_TYPE,
                f"Allowed types: {', '.join(sorted(LOADERS))}",)
    return loader(file_bytes)