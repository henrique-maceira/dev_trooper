import asyncio
import signal
import sys
import structlog

from .config import config
from .services.logging_service import setup_logging
try:
    from .telegram_bot import telegram_bot
except Exception as e:
    print(f"⚠️ Erro ao carregar bot real: {e}")
    print("🔄 Usando versão mock para demonstração...")
    from .telegram_bot_mock import telegram_bot

logger = structlog.get_logger(__name__)

class DevTrooperApp:
    """Aplicação principal do Dev Trooper"""
    
    def __init__(self):
        self.running = False
        self.telegram_bot = telegram_bot
    
    async def start(self):
        """Inicia a aplicação"""
        try:
            logger.info("🚀 Iniciando Dev Trooper - Sistema Multi-Agentes")
            
            # Validar configurações
            config.validate()
            logger.info("✅ Configurações validadas")
            
            # Configurar logging
            setup_logging()
            logger.info("✅ Logging configurado")
            
            # Configurar handlers de sinal
            self._setup_signal_handlers()
            
            # Iniciar bot do Telegram
            self.running = True
            logger.info("🤖 Iniciando bot do Telegram...")
            
            await self.telegram_bot.start()
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar aplicação: {e}")
            sys.exit(1)
    
    def _setup_signal_handlers(self):
        """Configura handlers para sinais do sistema"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Sinal {signum} recebido. Encerrando aplicação...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def stop(self):
        """Para a aplicação"""
        logger.info("🛑 Parando aplicação...")
        self.running = False

async def main():
    """Função principal"""
    app = DevTrooperApp()
    
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("👋 Aplicação interrompida pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)
    finally:
        app.stop()

if __name__ == "__main__":
    # Executar aplicação
    asyncio.run(main())
