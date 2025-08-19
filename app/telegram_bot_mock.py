import asyncio
import structlog

from .config import config
from .models.schemas import ProjectConfig, UserSession
from .models.state_store import state_store
from .agents.manager import manager_agent
from .agents.programmer import programmer_agent
from .services.logging_service import log_agent_action

logger = structlog.get_logger(__name__)

# Configurar agentes
manager_agent.set_programmer_agent(programmer_agent)

class MockTelegramBot:
    """Bot mock do Telegram para testes"""
    
    def __init__(self):
        logger.info("Iniciando bot mock do Telegram")
    
    async def start(self):
        """Inicia o bot mock"""
        logger.info("🤖 Bot mock do Dev Trooper iniciado!")
        logger.info("📱 Para usar o bot real, configure um token válido no .env")
        logger.info("🔧 Comandos disponíveis no bot real:")
        logger.info("   /start - Instruções iniciais")
        logger.info("   /projeto <nome> - Criar/selecionar projeto")
        logger.info("   /repo <url> - Configurar repositório")
        logger.info("   /tarefa <descrição> - Criar e executar tarefa")
        logger.info("   /status <task_id> - Verificar status")
        logger.info("   /ajuda - Ajuda completa")
        
        # Simular algumas operações de teste
        await self._demo_operations()
    
    async def _demo_operations(self):
        """Demonstra algumas operações do sistema"""
        try:
            logger.info("🧪 Executando demonstração do sistema...")
            
            # Criar projeto de teste
            project_config = ProjectConfig(
                name="demo-project",
                repo_url="https://github.com/user/demo-repo",
                default_branch="main",
                test_command="pytest -q"
            )
            
            # Salvar projeto
            if state_store.save_project(project_config):
                logger.info("✅ Projeto de demonstração criado")
            
            # Criar sessão de usuário
            session = UserSession(
                user_id=12345,
                current_project="demo-project"
            )
            state_store.save_session(session)
            
            # Criar task de demonstração
            task_description = "Adicionar função de exemplo"
            task = manager_agent.create_task(project_config, task_description)
            
            logger.info(f"✅ Task de demonstração criada: {task.id}")
            logger.info(f"📋 Objetivo: {task.objective}")
            
            # Simular implementação
            logger.info("🔄 Simulando implementação...")
            success, result, pr_url = manager_agent.review_and_iterate(task.id)
            
            if success:
                logger.info("🎉 Demonstração concluída com sucesso!")
                logger.info(f"📝 Resultado: {result}")
            else:
                logger.info("⚠️ Demonstração com ajustes necessários")
                logger.info(f"📝 Feedback: {result}")
            
        except Exception as e:
            logger.error(f"❌ Erro na demonstração: {e}")

# Instância global
telegram_bot = MockTelegramBot()
