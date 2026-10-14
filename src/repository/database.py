from  sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,async_sessionmaker
from  src.settings import Settings

settings = Settings()

engine = create_async_engine(
     settings.DB_URL,
    echo=False,
    pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_= AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
