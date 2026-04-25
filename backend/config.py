import os


class Config:

    OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    MODEL = os.getenv("MODEL", "openai/gpt-4o-mini")
    PROMTIOR_URL = os.getenv("PROMTIOR_URL", "https://www.promtior.ai")


config = Config()