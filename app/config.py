from typing import Optional, Any, Dict

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    # TODO Why is it Optional[str] instead of Optional[PostgresDsn]?
    # TODO Why is it Dict[str, any] instead of Dict[str, str]?
    def assemble_db_connection(
        cls, value: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(value, str):
            return value
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            # TODO why the condition? POSTGRES_DB is not Optional[str]?
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        case_sensitive = True


settings = Settings()
