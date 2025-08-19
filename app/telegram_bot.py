from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message
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

class TelegramBot:
    """Bot do Telegram para interação com o sistema multi-agentes"""
    
    def __init__(self):
        self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()
        self.router = Router()
        
        # Registrar handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Registra os handlers dos comandos"""
        self.router.message(Command("start"))(self.cmd_start)
        self.router.message(Command("projeto"))(self.cmd_projeto)
        self.router.message(Command("repo"))(self.cmd_repo)
        self.router.message(Command("tarefa"))(self.cmd_tarefa)
        self.router.message(Command("status"))(self.cmd_status)
        self.router.message(Command("ajuda"))(self.cmd_ajuda)
        
        self.dp.include_router(self.router)
    
    async def cmd_start(self, message: Message):
        """Comando /start - instruções iniciais"""
        welcome_text = """
🤖 Dev Trooper - Sistema Multi-Agentes

Bem-vindo! Eu sou um assistente de desenvolvimento que pode ajudar você a implementar funcionalidades automaticamente.

Comandos disponíveis:
• /projeto - Lista projetos ou cria/seleciona um projeto
• /repo - Mostra ou altera URL do repositório
• /tarefa <descrição> - Cria uma nova tarefa
• /status <task_id> - Verifica status de uma tarefa
• /ajuda - Mostra esta ajuda

Como usar:
1. Liste projetos: /projeto
2. Crie um projeto: /projeto meu-projeto
3. Crie uma tarefa: /tarefa Adicionar função de login

Vamos começar! 🚀
"""
        await message.answer(welcome_text)
    
    async def cmd_projeto(self, message: Message):
        """Comando /projeto - lista projetos ou cria/seleciona projeto"""
        try:
            args = message.text.split(maxsplit=1)
            user_id = message.from_user.id
            
            if len(args) < 2:
                # Listar projetos existentes
                projects = state_store.list_projects()
                if projects:
                    projects_text = "📋 Projetos disponíveis:\n\n"
                    for i, project in enumerate(projects, 1):
                        projects_text += f"{i}. {project}\n"
                    projects_text += "\nPara selecionar: /projeto <nome>\nPara criar novo: /projeto <nome>"
                    await message.answer(projects_text)
                else:
                    await message.answer("📋 Nenhum projeto encontrado.\nPara criar um projeto: /projeto <nome>")
                return
            
            project_name = args[1].strip()
            
            # Verificar se projeto já existe
            existing_project = state_store.get_project(project_name)
            
            if existing_project:
                # Projeto existe - selecionar
                state_store.update_session_project(user_id, project_name)
                
                # Gerar URL automática se não estiver configurada
                if not existing_project.repo_url:
                    repo_url = f"https://github.com/henrique-maceira/{project_name}"
                    existing_project.repo_url = repo_url
                    state_store.save_project(existing_project)
                    await message.answer(
                        f"✅ Projeto {project_name} selecionado!\n"
                        f"🔗 Repositório configurado: {repo_url}\n"
                        f"📝 Agora você pode criar tarefas com /tarefa <descrição>"
                    )
                else:
                    await message.answer(
                        f"✅ Projeto {project_name} selecionado!\n"
                        f"🔗 Repositório: {existing_project.repo_url}\n"
                        f"📝 Agora você pode criar tarefas com /tarefa <descrição>"
                    )
            else:
                # Criar novo projeto
                repo_url = f"https://github.com/henrique-maceira/{project_name}"
                project_config = ProjectConfig(
                    name=project_name,
                    repo_url=repo_url,
                    default_branch="main",
                    test_command="pytest -q"
                )
                
                if state_store.save_project(project_config):
                    state_store.update_session_project(user_id, project_name)
                    await message.answer(
                        f"✅ Projeto {project_name} criado!\n"
                        f"🔗 Repositório: {repo_url}\n"
                        f"📝 Agora você pode criar tarefas com /tarefa <descrição>"
                    )
                else:
                    await message.answer("❌ Erro ao criar projeto")
                    
        except Exception as e:
            logger.error(f"Erro no comando projeto: {e}")
            await message.answer("❌ Erro interno ao processar comando")
    
    async def cmd_repo(self, message: Message):
        """Comando /repo - define URL do repositório (opcional)"""
        try:
            args = message.text.split(maxsplit=1)
            user_id = message.from_user.id
            
            # Verificar se usuário tem projeto selecionado
            session = state_store.get_session(user_id)
            if not session or not session.current_project:
                await message.answer("❌ Nenhum projeto selecionado. Use /projeto <nome> primeiro")
                return
            
            if len(args) < 2:
                # Mostrar repositório atual
                project_config = state_store.get_project(session.current_project)
                if project_config and project_config.repo_url:
                    await message.answer(
                        f"🔗 Repositório atual:\n"
                        f"Projeto: {session.current_project}\n"
                        f"URL: {project_config.repo_url}\n\n"
                        f"Para alterar: /repo <nova_url>"
                    )
                else:
                    await message.answer("❌ Repositório não configurado. Use /repo <url>")
                return
            
            repo_url = args[1].strip()
            
            # Atualizar configuração do projeto
            project_config = state_store.get_project(session.current_project)
            if not project_config:
                await message.answer("❌ Projeto não encontrado")
                return
            
            project_config.repo_url = repo_url
            if state_store.save_project(project_config):
                await message.answer(
                    f"✅ Repositório configurado!\n"
                    f"Projeto: {session.current_project}\n"
                    f"URL: {repo_url}\n\n"
                    f"Agora você pode criar tarefas com /tarefa <descrição>"
                )
            else:
                await message.answer("❌ Erro ao salvar configuração do repositório")
                
        except Exception as e:
            logger.error(f"Erro no comando repo: {e}")
            await message.answer("❌ Erro interno ao processar comando")
    
    async def cmd_tarefa(self, message: Message):
        """Comando /tarefa - cria nova tarefa"""
        try:
            args = message.text.split(maxsplit=1)
            if len(args) < 2:
                await message.answer("❌ Uso: `/tarefa <descrição da tarefa>`", parse_mode="Markdown")
                return
            
            task_description = args[1].strip()
            user_id = message.from_user.id
            
            # Verificar se usuário tem projeto configurado
            session = state_store.get_session(user_id)
            if not session or not session.current_project:
                await message.answer("❌ Nenhum projeto selecionado. Use `/projeto <nome>` primeiro")
                return
            
            project_config = state_store.get_project(session.current_project)
            if not project_config:
                await message.answer("❌ Projeto não encontrado")
                return
            
            if not project_config.repo_url:
                await message.answer("❌ Repositório não configurado. Use /repo <url> primeiro")
                return
            
            # Enviar mensagem de processamento
            processing_msg = await message.answer("🔄 Processando tarefa...")
            
            try:
                # Criar task
                task = manager_agent.create_task(project_config, task_description)
                
                # Atualizar mensagem
                await processing_msg.edit_text(
                    f"✅ Task criada!\n\n"
                    f"ID: {task.id}\n"
                    f"Objetivo: {task.objective}\n"
                    f"Status: {task.status.value}\n\n"
                    f"🔄 Iniciando implementação..."
                )
                
                # Executar implementação
                success, result, pr_url = manager_agent.review_and_iterate(task.id)
                
                if success:
                    await processing_msg.edit_text(
                        f"🎉 Task concluída com sucesso!\n\n"
                        f"ID: {task.id}\n"
                        f"Objetivo: {task.objective}\n"
                        f"Status: {task.status.value}\n"
                        f"PR: {pr_url or 'N/A'}\n\n"
                        f"✅ Implementação aprovada e PR criado!"
                    )
                else:
                    await processing_msg.edit_text(
                        f"⚠️ Task precisa de ajustes\n\n"
                        f"ID: {task.id}\n"
                        f"Objetivo: {task.objective}\n"
                        f"Status: {task.status.value}\n\n"
                        f"Feedback:\n{result}"
                    )
                    
            except Exception as e:
                logger.error(f"Erro ao processar tarefa: {e}")
                await processing_msg.edit_text(
                    f"❌ Erro ao processar tarefa\n\n"
                    f"Erro: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"Erro no comando tarefa: {e}")
            await message.answer("❌ Erro interno ao processar comando")
    
    async def cmd_status(self, message: Message):
        """Comando /status - verifica status de uma tarefa"""
        try:
            args = message.text.split(maxsplit=1)
            if len(args) < 2:
                await message.answer("❌ Uso: /status <task_id>")
                return
            
            task_id = args[1].strip()
            task = state_store.get_task(task_id)
            
            if not task:
                await message.answer("❌ Task não encontrada")
                return
            
            # Formatar histórico
            history_text = ""
            for event in task.history[-5:]:  # Últimos 5 eventos
                history_text += f"• {event.timestamp.strftime('%H:%M:%S')} - {event.message}\n"
            
            status_text = f"""
📋 Status da Task

ID: {task.id}
Projeto: {task.project}
Objetivo: {task.objective}
Status: {task.status.value}
Criada: {task.created_at.strftime('%d/%m/%Y %H:%M:%S')}

Histórico recente:
{history_text}
"""
            await message.answer(status_text)
            
        except Exception as e:
            logger.error(f"Erro no comando status: {e}")
            await message.answer("❌ Erro interno ao processar comando")
    
    async def cmd_ajuda(self, message: Message):
        """Comando /ajuda - mostra ajuda"""
        help_text = """
📚 Ajuda - Dev Trooper

Comandos principais:

🔧 Configuração:
• /projeto - Lista projetos ou cria/seleciona um projeto
• /repo - Mostra ou altera URL do repositório GitHub

📝 Tarefas:
• /tarefa <descrição> - Cria e executa uma nova tarefa
• /status <task_id> - Verifica status de uma tarefa

ℹ️ Informações:
• /ajuda - Mostra esta ajuda
• /start - Reinicia o bot

Exemplos de uso:
/projeto meu-app
/repo https://github.com/henrique-maceira/meu-app
/tarefa Adicionar função de login
/status abc12345-def6-7890-ghij-klmnopqrstuv

Fluxo típico:
1. Criar projeto → /projeto nome
2. Criar tarefa → /tarefa descrição
3. Acompanhar → /status task_id

🤖 O sistema irá:
- Analisar sua solicitação
- Gerar especificação técnica
- Implementar as mudanças
- Executar testes
- Criar Pull Request
"""
        await message.answer(help_text)
    
    async def start(self):
        """Inicia o bot"""
        logger.info("Iniciando bot do Telegram...")
        await self.dp.start_polling(self.bot)

# Instância global
telegram_bot = TelegramBot()
