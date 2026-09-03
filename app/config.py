from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    github_token: str
    github_owner: str
    github_repo: str
    webhook_secret: str
    port: int = 8000

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()