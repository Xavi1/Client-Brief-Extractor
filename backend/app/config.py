from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Core Model configurations
    MODEL_API_KEY: str
    MODEL_NAME: str = "gpt-4o"  # Set a default value if you want

    # Automatically read from a .env file if it exists
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Prevents crashing if extra vars exist in .env
    )

# Instantiate the settings object to be imported elsewhere
settings = Settings()
