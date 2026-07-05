import os


class Settings:
    def __init__(self):
        self._loaded = False

    def _load_env(self):
        if self._loaded:
            return
        # Try loading from .env file
        dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.isfile(dotenv_path):
            with open(dotenv_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, val = line.partition("=")
                    key, val = key.strip(), val.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = val
        self._loaded = True

    @property
    def llm_backend(self) -> str:
        self._load_env()
        return os.environ.get("LLM_BACKEND", "mock").lower()

    @property
    def deepseek_api_key(self) -> str | None:
        self._load_env()
        return os.environ.get("DEEPSEEK_API_KEY") or None

    @property
    def deepseek_model(self) -> str:
        self._load_env()
        return os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

    @property
    def zhipuai_api_key(self) -> str | None:
        self._load_env()
        return os.environ.get("ZHIPUAI_API_KEY") or None

    @property
    def zhipuai_model(self) -> str:
        self._load_env()
        return os.environ.get("ZHIPUAI_MODEL", "glm-4")


settings = Settings()
