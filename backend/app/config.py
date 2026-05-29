from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Detection backend. Set DETECTION_MODE in env (or .env) to switch.
    #   "yolo"   — YOLO-World open-vocabulary + HSV vest analysis (fast, no LLM)
    #   "gemini" — YOLO-World person detection + Google Gemini 2.5 Flash VLM
    detection_mode: str = "gemini"

    gemini_api_key: str = ""
    # Gemini model id. Override with GEMINI_MODEL in .env (e.g. gemini-2.0-flash
    # or gemini-2.5-flash-lite, which have more generous free-tier rate limits).
    gemini_model: str = "gemini-2.5-flash"

    yolo_model: str = "yolov8l-world.pt"
    upload_dir: str = "uploads"
    static_dir: str = "static"
    confidence_threshold: float = 0.35
    max_upload_size_mb: int = 10

    # Comma-separated list of allowed CORS origins for the split deploy
    # (frontend on Vercel calling this backend on another host). Add your
    # Vercel URL via CORS_ORIGINS, e.g. "https://visionai.vercel.app".
    # Use "*" to allow any origin.
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:8000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

