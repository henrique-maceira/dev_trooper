import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações da aplicação carregadas de variáveis de ambiente"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    
    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    # Diretórios
    WORKDIR_BASE = Path(os.getenv("WORKDIR_BASE", "/tmp/dev_trooper"))
    ARTIFACTS_DIR = Path("artifacts")
    
    # Git
    DEFAULT_GIT_AUTHOR = os.getenv("DEFAULT_GIT_AUTHOR", "Agent Bot <agent@example.com>")
    
    @classmethod
    def validate(cls):
        """Valida se todas as configurações obrigatórias estão presentes"""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "OPENAI_API_KEY", 
            "GITHUB_TOKEN"
        ]
        
        missing = []
        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing)}")
        
        # Criar diretórios se não existirem
        cls.WORKDIR_BASE.mkdir(parents=True, exist_ok=True)
        cls.ARTIFACTS_DIR.mkdir(exist_ok=True)
        
        return True

# Instância global
config = Config()
