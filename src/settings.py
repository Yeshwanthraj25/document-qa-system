from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DB_URL: str
    MAX_UPLOAD_SIZE_MB: int = 10
    CLOUDFLARE_ACCOUNT_ID: str = ""
    CLOUDFLARE_API_TOKEN: str = ""
    EMBEDDING_MODEL: str = "@cf/baai/bge-base-en-v1.5"
    EMBEDDING_DIMENSION: int = 768
    EMBEDDING_BATCH_SIZE: int = 16
    MAX_RETRIES: int  = 3
    RETRYABLE_STATUS:set[int] = {429, 500, 502, 503, 504}
    QUERY_PREFIX: str  = "Represent this sentence for searching relevant passages: "
    LLM_MODEL: str = "@cf/meta/llama-3.1-8b-instruct"
    LLM_MAX_TOKENS: int = 512
    LLM_TEMPERATURE: float = 0.0
    MIN_RELEVANCE_SCORE:float = 0.45
    
   
    
    model_config = ConfigDict(env_file=".env")  

settings = Settings()


