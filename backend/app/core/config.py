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

    # AI provider selection — "ollama" (local dev default) or "groq" (production)
    ai_provider: str = "ollama"  # NEW

    # AI / Ollama configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: float = 600.0
    ollama_num_ctx: int = 8192

    # AI / Groq configuration — only used when ai_provider == "groq"
    groq_api_key: str = ""                                # NEW
    groq_model: str = "openai/gpt-oss-20b"                 # NEW
    groq_timeout_seconds: float = 30.0                     # NEW
    groq_chunk_pacing_seconds: float = 30.0                 # NEW — delay between chunk calls to stay under Groq's TPM limit

    # Upload / document limits
    max_upload_size_mb: float = 10.0
    chunk_threshold_chars: int = 12000
    max_extracted_chars: int = 200000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()