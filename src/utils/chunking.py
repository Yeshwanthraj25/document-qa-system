
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
   

