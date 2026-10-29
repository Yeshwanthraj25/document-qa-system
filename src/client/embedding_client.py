import asyncio
import logging

import httpx

from src.settings import settings
from src.utils.exceptions.custom_exceptions import ClientError
from src.utils.exceptions.error_codes import ErrorCode

logger = logging.getLogger(__name__)




def _api_url() -> str:
    return (f"https://api.cloudflare.com/client/v4/accounts/"
            f"{settings.CLOUDFLARE_ACCOUNT_ID}/ai/run/{settings.EMBEDDING_MODEL}")



async def embed_texts(texts: list[str]) -> list[list[float]]:
  """Returns one vector per text, in the same order."""
  if not texts:
    return []

  if not settings.CLOUDFLARE_ACCOUNT_ID or not settings.CLOUDFLARE_API_TOKEN:
    raise ClientError(
        ErrorCode.EMBEDDING_FAILED, "Embedding service is not configured"
    )

  batch_size = settings.EMBEDDING_BATCH_SIZE
  vectors = []

  async with httpx.AsyncClient(timeout=30.0) as client:
    for i in range(0, len(texts), batch_size):
      batch = texts[i : i + batch_size]
      batch_vectors = await _embed_batch(client, batch)
      vectors.extend(batch_vectors)

  return vectors

async def _embed_batch(client: httpx.AsyncClient, batch: list[str]) -> list[list[float]]:
    last_error = None
    for attempt in range(settings.MAX_RETRIES):
        try:
            response = await client.post(
                            _api_url(),
                            headers={"Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}"},
                            json={"text": batch},
                        )            
        except httpx.TransportError as exc:
            last_error = exc
            await asyncio.sleep(2 ** attempt)
            continue
        if response.status_code in settings.RETRYABLE_STATUS:
            await asyncio.sleep(2 ** attempt)
            continue

        if response.status_code != 200:
                    raise ClientError(ErrorCode.EMBEDDING_FAILED, f"Embedding request failed ({response.status_code})")
        try:
            body = response.json()
            vectors = body["result"]["data"]
        except (ValueError, KeyError, TypeError) as exc:
            raise ClientError(ErrorCode.EMBEDDING_FAILED, "Unexpected embedding response") from exc
        if not body.get("success") or len(vectors) != len(batch) or any(len(v) != settings.EMBEDDING_DIMENSION for v in vectors):
            raise ClientError(ErrorCode.EMBEDDING_FAILED, "Unexpected embedding response")
        return vectors

    raise ClientError(ErrorCode.EMBEDDING_FAILED, "Embedding service unavailable after retries") from last_error