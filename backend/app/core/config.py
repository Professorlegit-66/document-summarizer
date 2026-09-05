from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Central application configuration.

    Values are loaded from environment variables (or a local .env file
    during development). Never hard-code secrets or environment-specific
    values elsewhere in the app — add a field here instead.
    """

    app_name: str = "Document Summarizer API"
    debug: bool = False
    frontend_origin: str = "http://localhost:5173"

    # AI / Ollama configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: float = 120.0

    # Upload / document limits
    max_upload_size_mb: float = 10.0
    max_extracted_chars: int = 12000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()