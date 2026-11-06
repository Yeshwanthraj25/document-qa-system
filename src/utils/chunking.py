from src.settings import settings
def chunking(text:str,chunk_size: int = 1000 , overlap: int=200) -> list[tuple[int,int,str]]: 
        if overlap >= chunk_size:
              raise ValueError("overlap must be smaller than chunk_size")
        if not text:
            return []
        step = chunk_size - overlap 
        chunk = []
        start = 0
        while overlap < chunk_size:
            end = min(start + chunk_size , len(text))
            chunk.append((start,end,text[start:end]))
            if end == len(text):
                break
            start += step
        return chunk
   

from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunking_recursive(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[tuple[int, int, str]]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    if not text:
        return []
    splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            add_start_index=True,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    docs = splitter.create_documents([text])
    return [(d.metadata["start_index"],
                d.metadata["start_index"] + len(d.page_content),
                d.page_content) for d in docs]

def split_text(text: str) -> list[tuple[int, int, str]]:
    if settings.CHUNKING_STRATEGY == "recursive":
        return chunking_recursive(text)
    return chunking(text)