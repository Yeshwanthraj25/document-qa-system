
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DB_URL: str
    MAX_UPLOAD_SIZE_MB: int = 10
   
    
    model_config = ConfigDict(env_file=".env")  

settings = Settings()