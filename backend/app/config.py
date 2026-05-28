from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Detection backend. Set DETECTION_MODE in env (or .env) to switch.
    #   "yolo"   — YOLO-World open-vocabulary + HSV vest analysis (fast, no LLM)
    #   "ollama" — YOLO-World person detection + Ollama VLM per worker
    detection_mode: str = "yolo"

    ollama_url: str = "http://localhost:11434"
    # Vision-language model used when detection_mode="ollama".
    # gemma3:4b fits a 6 GB VRAM GPU fully and gives reliable VQA outputs.
    ollama_model: str = "gemma3:4b"
    # Legacy alias kept so old .env files still load
    llava_model: str = "gemma3:4b"

    yolo_model: str = "yolov8l-world.pt"
    upload_dir: str = "uploads"
    static_dir: str = "static"
    confidence_threshold: float = 0.35
    max_upload_size_mb: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
