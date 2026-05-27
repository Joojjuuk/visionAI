from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    llava_model: str = "llava:7b"
    yolo_model: str = "yolov8n.pt"
    upload_dir: str = "uploads"
    static_dir: str = "static"
    confidence_threshold: float = 0.50
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
