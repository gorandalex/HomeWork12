from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://postgres:567234@localhost:5432/postgres'
    secret_key: str = "secret_key"
    algorithm: str = "HS256"
    mail_username: str = "example@example.com"
    mail_password: str = "password"
    mail_from: str = "example@example.com"
    mail_port: int = 465
    mail_server: str = "smtp.example.com"
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str = 'cloudinary_name'
    cloudinary_api_key: str = 'cloudinary_api_key'
    cloudinary_api_secret: str = 'cloudinary_api_secret'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"




settings = Settings()