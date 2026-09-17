from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://peeripo:peeripo@localhost:5432/peeripo"
    token_encryption_key: str = "change-me-32-byte-key-please!!"

    class Config:
        env_file = ".env"


settings = Settings()
