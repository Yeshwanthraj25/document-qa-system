
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
   
    
    model_config = ConfigDict(env_file=".env")  

settings = Settings()


