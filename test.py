import asyncio
from src.client.embedding_client import embed_texts

vectors = asyncio.run(embed_texts(["hello world", "python backend"]))
print(len(vectors), len(vectors[0]))